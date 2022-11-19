import logging
from typing import List, Any, Dict

from autologging import traced
from email_validator import EmailNotValidError, validate_email
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
		print(self.conn.__dict__)

	def obstaja(self, email: str):
		try:
			validation = validate_email(email=email, check_deliverability=True, timeout=1)
			log.info(validation.__dict__)
			return True
		except EmailNotValidError as e:
			log.warning(e)
			return False

	async def send(self, recipients: List[str], subject: str, vsebina: str):
		message = MessageSchema(
			recipients=[EmailStr(r) for r in recipients],
			body=vsebina,
			subject=subject,
			subtype=MessageType.html)

		await FastMail(self.conn).send_message(message)
