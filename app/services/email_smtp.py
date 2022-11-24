import logging
from ipaddress import IPv4Address, IPv6Address
from typing import List, Any, Dict

from autologging import traced
from fastapi_mail import ConnectionConfig, MessageType, MessageSchema, FastMail
from pydantic import BaseModel, EmailStr
from validate_email import validate_email

from core import cutils
from core.services.email_service import EmailService

log = logging.getLogger(__name__)


class EmailSchema(BaseModel):
	email: List[EmailStr]
	body: Dict[str, Any]


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
		self.inst = FastMail(self.conn)

	def obstaja(self, email: str):
		return validate_email(
			email_address=email,
			check_format=True,
			check_blacklist=True,
			check_dns=not self.conn.SUPPRESS_SEND,
			check_smtp=not self.conn.SUPPRESS_SEND,
			dns_timeout=5,
			smtp_timeout=5,
			smtp_helo_host=self.conn.MAIL_SERVER,
			smtp_from_address=self.conn.MAIL_FROM,
			smtp_skip_tls=False,
			smtp_tls_context=None,
			smtp_debug=True,
			address_types=frozenset([IPv4Address, IPv6Address]))

	async def send(self, recipients: List[str], subject: str, vsebina: str):
		message = MessageSchema(
			recipients=[EmailStr(r) for r in recipients],
			body=vsebina,
			subject=subject,
			subtype=MessageType.html)

		await self.inst.send_message(message)
