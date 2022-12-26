import logging
from ipaddress import IPv4Address, IPv6Address
from typing import List, Any, Dict

from autologging import traced
from fastapi_mail import ConnectionConfig, MessageType, MessageSchema, FastMail
from imap_tools import MailBox
from pydantic import BaseModel, EmailStr
from validate_email import validate_email

from core import cutils
from core.services.email_service import EmailService, EmailPerson, Email, EmailFlag, EmailFolderStatus

log = logging.getLogger(__name__)


class EmailSchema(BaseModel):
	email: List[EmailStr]
	body: Dict[str, Any]


@traced
class Email_smtp_imap(EmailService):
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
		self.imap = MailBox(server)
		self.imap.login(username=username, password=password, initial_folder='INBOX')

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

	def delete(self, id: str) -> bool:
		r, e = self.imap.delete(uid_list=[id])
		return r[0] == 'OK' and e[0] == 'OK'

	def get_all(self) -> list[Email]:
		mails = []
		for msg in self.imap.fetch():
			from_value = msg.from_values
			person = EmailPerson(email=from_value.email, name=from_value.name)
			mail = Email(
				id=msg.uid,
				sender=person,
				subject=msg.subject,
				content=msg.html,
				created=msg.date,
				flags=[EmailFlag.parse(flag) for flag in msg.flags])
			mails.append(mail)
		return mails

	def inbox_status(self) -> EmailFolderStatus:
		return self.folder_status(folder='INBOX')

	def folder_status(self, folder: str) -> EmailFolderStatus:
		stats = self.imap.folder.status(folder=folder)
		return EmailFolderStatus(
			messages=stats['MESSAGES'],
			recent=stats['RECENT'],
			unseen=stats['UNSEEN'])
