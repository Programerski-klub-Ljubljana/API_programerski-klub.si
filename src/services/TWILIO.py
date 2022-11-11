import sys

from twilio.rest import Client

from src import env

this = sys.modules[__name__]
this.client: Client


def init():
	this.client = Client(env.TWILIO_ACCOUNT_SID, env.TWILIO_AUTH_TOKEN)


def exist(phone_number: str) -> bool:
	phone_number = phone_number.strip()
	if not phone_number.startswith('+'):
		phone_number = f'+386{phone_number}'
	try:
		this.client.lookups.phone_numbers(phone_number).fetch()
		return True
	except Exception as err:
		return False
