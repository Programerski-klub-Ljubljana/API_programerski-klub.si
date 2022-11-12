from twilio.rest import Client

from core.services.sms_service import SmsService


class Twilio(SmsService):

	def __init__(self, account_sid: str, auth_token: str):
		self.client = Client(account_sid, auth_token)

	def poslji(self):
		print('poslji sms')

	def obstaja(self, phone: str) -> bool:
		phone = phone.strip()
		try:
			self.client.lookups.phone_numbers(phone).fetch()
			return True
		except Exception as err:
			return False
