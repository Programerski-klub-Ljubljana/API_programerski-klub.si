import datetime
import unittest
from unittest.mock import Mock

from app import app
from core.domain.arhitektura_kluba import Clan, Dovoljenja
from core.services.email_service import EmailService
from core.services.sms_service import SmsService
from core.services.utils import Validation
from core.use_cases.validation import ValidateClan


class test_validate_clan(unittest.TestCase):

	def setUp(self) -> None:
		app.init()

		# MOCKS
		self.clan: Clan = Mock(Clan)
		self.clan.email = 'email'
		self.clan.telefon = 'telefon'

		self.email_service: EmailService = Mock(EmailService)
		self.email_service.obstaja.return_value = Validation(data=, ok=True)
		self.sms_service: SmsService = Mock(SmsService)
		self.sms_service.obstaja.return_value = Validation(data='sms_service', ok=True)

		# SETUP
		# self.validation.ok = True
		# self.validation.data = 'data'
		# self.sms_service.obstaja.return_value = self.validation
		# self.email_service.obstaja.return_value = self.validation

		self.use_case = ValidateClan(emailService=self.email_service, smsService=self.sms_service)

	def test_vpis_clana(self):
		validations = self.use_case.invoke(self.clan)

		for validation in validations:
			self.assertIsInstance(validation, Validation)
			self.assertEqual(validation)


if __name__ == '__main__':
	unittest.main()
