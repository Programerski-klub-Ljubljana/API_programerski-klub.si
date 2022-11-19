import logging

import phonenumbers
from autologging import traced
from phonenumbers import NumberParseException
from twilio.rest import Client

from core.services.phone_service import PhoneService

log = logging.getLogger(__name__)


@traced
class Twilio(PhoneService):
	def __init__(self, account_sid: str, auth_token: str, default_country_code: str):
		self.default_country_code = default_country_code
		self.client = Client(account_sid, auth_token)

	def obstaja(self, phone: str) -> bool:
		try:
			phone_obj = phonenumbers.parse(phone, self.default_country_code)
			if phonenumbers.is_valid_number(phone_obj):
				phone = phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164)
				self.client.lookups.phone_numbers(phone).fetch()
				return True
		except Exception as err:
			log.warning(err)
		return False

	def parse(self, phone: str) -> str:
		try:
			x = phonenumbers.parse(phone, self.default_country_code)
			return phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.E164)
		except NumberParseException as err:
			log.warning(err)
			return phone
