from os import environ
from typing import List, Any, Dict

from fastapi_mail import ConnectionConfig, MessageType, MessageSchema, FastMail
from pydantic import BaseModel, EmailStr

from src import utils


class EmailSchema(BaseModel):
	email: List[EmailStr]
	body: Dict[str, Any]


conf = ConnectionConfig(
	MAIL_PASSWORD=environ['MAIL_PASSWORD'],
	MAIL_USERNAME="info@programerski-klub.si",
	MAIL_FROM="info@programerski-klub.si",
	MAIL_PORT=465,
	MAIL_SERVER="programerski-klub.si",
	MAIL_FROM_NAME="Programerski klub Ljubljana",
	MAIL_STARTTLS=False,
	MAIL_SSL_TLS=True,
	USE_CREDENTIALS=True,
	VALIDATE_CERTS=True,
	TEMPLATE_FOLDER=str(utils.root_path('templates')),
)


async def send(recipients: List[str], subject: str, vsebina: str):
	message = MessageSchema(
		recipients=[EmailStr(r) for r in recipients],
		body=vsebina,
		subject=subject,
		subtype=MessageType.html)

	await FastMail(conf).send_message(message)
