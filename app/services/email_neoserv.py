import logging
import smtplib
from typing import List, Any, Dict

import dns
from autologging import traced
from fastapi_mail import ConnectionConfig, MessageType, MessageSchema, FastMail
from pydantic import BaseModel, EmailStr

from core import cutils
from core.services.email_service import EmailService

log = logging.getLogger(__name__)


class EmailSchema(BaseModel):
	email: List[EmailStr]
	body: Dict[str, Any]


@traced
class SmtpEmail(EmailService):
	def __init__(self, name: str, email: str, server: str, port: str, username: str, password: str):
		self.conn = ConnectionConfig(
			MAIL_FROM_NAME=name, MAIL_FROM=email,
			MAIL_SERVER=server, MAIL_PORT=port,
			MAIL_PASSWORD=password, MAIL_USERNAME=username,
			MAIL_STARTTLS=False, MAIL_SSL_TLS=True,
			USE_CREDENTIALS=True, VALIDATE_CERTS=True,
			TEMPLATE_FOLDER=str(cutils.root_path('templates')))

	def obstaja(self, email: str):
		try:
			# Get domain for DNS lookup
			splitAddress = email.split('@')
			domain = splitAddress[-1]

			# MX record lookup
			records = dns.resolver.resolve(domain, 'MX')
			mxRecord = records[0].exchange
			mxRecord = str(mxRecord)

			# SMTP lib setup (use debug level for full output)
			server = smtplib.SMTP()
			server.set_debuglevel(0)

			server.connect(mxRecord)
			server.helo(server.local_hostname)
			server.mail(self.conn.MAIL_FROM)
			code, message = server.rcpt(email)
			server.quit()

			return code == 250

		except dns.resolver.NXDOMAIN as err:
			log.error(err)
			return False

		except Exception as err:
			log.error(err)
			return False

	async def send(self, recipients: List[str], subject: str, vsebina: str):
		message = MessageSchema(
			recipients=[EmailStr(r) for r in recipients],
			body=vsebina,
			subject=subject,
			subtype=MessageType.html)

		await FastMail(self.conn).send_message(message)
