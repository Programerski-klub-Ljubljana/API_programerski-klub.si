import email
import imaplib
import logging
import re
from ipaddress import IPv4Address, IPv6Address
from typing import List, Any, Dict

from autologging import traced
from fastapi_mail import ConnectionConfig, MessageType, MessageSchema, FastMail
from pydantic import BaseModel, EmailStr
from validate_email import validate_email

from core import cutils
from core.services.email_service import EmailService, Email, EmailPerson

log = logging.getLogger(__name__)


class EmailSchema(BaseModel):
	email: List[EmailStr]
	body: Dict[str, Any]


class SmtpPerson(EmailPerson):
	@staticmethod
	def parse(data: str):
		e_mail = re.findall(pattern='\<(.*?)>', string=data)
		if len(e_mail) == 1:
			return EmailPerson(email=e_mail[0], name=data.replace(f' <{e_mail[0]}>', '').strip())


@traced
class EmailSmtp(EmailService):
	def __init__(self, name: str, email: str, server: str, port: str, username: str, password: str, suppress_send: bool):
		self.conn = ConnectionConfig(
			MAIL_FROM_NAME=name, MAIL_FROM=email,
			MAIL_SERVER=server, MAIL_PORT=port,
			MAIL_PASSWORD=password, MAIL_USERNAME=username,
			MAIL_STARTTLS=False, MAIL_SSL_TLS=True,
			USE_CREDENTIALS=True, VALIDATE_CERTS=True,
			SUPPRESS_SEND=suppress_send,
			TEMPLATE_FOLDER=str(cutils.root_path('templates')))

		self.fmail = FastMail(self.conn)
		self.mail = imaplib.IMAP4_SSL(server)
		self.mail.login(user=email, password=password)

	def check_existance(self, email: str):
		return validate_email(
			email_address=email,
			check_format=True,
			check_blacklist=True,
			check_dns=not self.conn.SUPPRESS_SEND,
			check_smtp=False,
			dns_timeout=3,
			address_types=frozenset([IPv4Address, IPv6Address]))

	async def send(self, recipients: List[str], subject: str, vsebina: str):
		message = MessageSchema(
			recipients=[EmailStr(r) for r in recipients],
			body=vsebina,
			subject=subject,
			subtype=MessageType.html)

		await self.fmail.send_message(message)

	def mailbox(self) -> list[Email]:
		self.mail.select('inbox')

		status, data = self.mail.search(None, 'ALL')
		mail_ids = []
		for block in data:
			mail_ids += block.split()

		all_emails = []
		for i in mail_ids:
			status, data = self.mail.fetch(i, '(RFC822)')
			for response_part in data:
				if isinstance(response_part, tuple):
					e = Email()
					message = email.message_from_bytes(response_part[1])
					e.sender = SmtpPerson.parse(data=message['from'])
					e.subject = message['subject']

					if message.is_multipart():
						e.content = ''
						for part in message.get_payload():
							if part.get_content_type() == 'text/plain':
								e.content += part.get_payload()
					else:
						e.content = message.get_payload()

					all_emails.append(e)
		return all_emails
