import logging

import phonenumbers
from autologging import traced
from countryinfo import CountryInfo
from phonenumbers import NumberParseException
from twilio.rest import Client
from twilio.rest.api.v2010.account.message import MessageInstance

from core.services.phone_service import PhoneService, PhoneOrigin

log = logging.getLogger(__name__)


@traced
class PhoneTwilio(PhoneService):
	success_statuses = [
		MessageInstance.Status.ACCEPTED,
		MessageInstance.Status.QUEUED,
		MessageInstance.Status.SENDING,
		MessageInstance.Status.SENT,
		MessageInstance.Status.DELIVERED,
		MessageInstance.Status.RECEIVED
	]

	def __init__(self, service_sid: str, account_sid: str, auth_token: str, default_country_code: str, from_number: str):
		self.default_country_code = default_country_code
		self.from_number = from_number
		self.service_sid = service_sid
		self.client = Client(account_sid, auth_token)

	def check_existance(self, phone: str) -> bool:
		try:
			phone_obj = phonenumbers.parse(number=phone, region=self.default_country_code)
			if phonenumbers.is_valid_number(phone_obj):
				phone = phonenumbers.format_number(numobj=phone_obj, num_format=phonenumbers.PhoneNumberFormat.E164)
				self.client.lookups.phone_numbers(phone).fetch()
				return True
		except Exception as err:
			log.warning(err)
		return False

	def origin(self, phone: str) -> PhoneOrigin:
		phone_obj = phonenumbers.parse(number=phone, region=self.default_country_code)
		country = CountryInfo(phone_obj.country_code)
		return PhoneOrigin(
			timezone=country.timezones()[0],
			languages=country.languages(),
			country=country.iso(2),
			name=country.native_name()
		)

	def format(self, phone: str) -> str:
		try:
			x = phonenumbers.parse(phone, self.default_country_code)
			return phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.E164)
		except NumberParseException as err:
			log.warning(err)
			return phone

	def send_sms(self, phone: str, text: str) -> bool:
		# TODO: LOG sms status.
		sms = self.client.messages.create(to=phone, body=text, messaging_service_sid=self.service_sid)
		return sms.status in self.success_statuses
