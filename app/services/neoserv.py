import sys
from typing import List, Any, Dict

import requests
from fastapi_mail import ConnectionConfig, MessageType, MessageSchema, FastMail
from pydantic import BaseModel, EmailStr

from api import utils
from app import env
from core.services.email_service import EmailService
from core.services._utils import Validation


class NeoServ(EmailService):

	def obstaja(self, email):
		response = requests.get(
			"https://isitarealemail.com/api/email/validate",
			params={'email': email},
			headers={'Authorization': f"Bearer {env.IS_REAL_EMAIL_BEARER}"})

		status = response.json()['status']
		return status == 'valid'

	def poslji(self):
		pass


class EmailSchema(BaseModel):
	email: List[EmailStr]
	body: Dict[str, Any]


this = sys.modules[__name__]
this.connection: ConnectionConfig


def init():
	this.connection = ConnectionConfig(
		MAIL_PASSWORD=env.MAIL_PASSWORD,
		MAIL_USERNAME="info@programerski-klub.si",
		MAIL_FROM="info@programerski-klub.si",
		MAIL_PORT=465,
		MAIL_SERVER="programerski-klub.si",
		MAIL_FROM_NAME="Programerski klub Ljubljana",
		MAIL_STARTTLS=False,
		MAIL_SSL_TLS=True,
		USE_CREDENTIALS=True,
		VALIDATE_CERTS=True,
		TEMPLATE_FOLDER=str(utils.root_path('templates')))


async def send(recipients: List[str], subject: str, vsebina: str):
	message = MessageSchema(
		recipients=[EmailStr(r) for r in recipients],
		body=vsebina,
		subject=subject,
		subtype=MessageType.html)

	await FastMail(this.connection).send_message(message)
