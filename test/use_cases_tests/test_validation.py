import unittest
from unittest.mock import Mock

from app import app
from core.domain.arhitektura_kluba import Clan, Kontakt
from core.services.email_service import EmailService
from core.services.sms_service import SmsService
from core.use_cases.validation_cases import Validate_clan, Validate_kontakt


class test_validate(unittest.TestCase):

	def setUp(self) -> None:
		app.init(True)

		# MOCKS
		self.clan: Clan = Mock(Clan)
		self.kontakt: Kontakt = Mock(Kontakt)

		self.email_service: EmailService = Mock(EmailService)
		self.email_service.obstaja.return_value = True
		self.sms_service: SmsService = Mock(SmsService)
		self.sms_service.obstaja.return_value = True

		# USE CASE
		self.validate_clan = Validate_clan(emailService=self.email_service, smsService=self.sms_service)
		self.validate_kontakt = Validate_kontakt(emailService=self.email_service, smsService=self.sms_service)

	def test_validate_clan(self):
		validations = self.validate_clan.invoke(self.clan)
		oks = [val.ok for val in validations]
		datas = [val.data for val in validations]
		self.assertListEqual([self.clan.telefon, self.clan.email], datas)  # Should check only telephone and email.
		self.assertListEqual([True, True], oks)

	def test_validate_kontakt(self):
		validations = self.validate_kontakt.invoke(self.kontakt)
		oks = [val.ok for val in validations]
		datas = [val.data for val in validations]
		self.assertListEqual([self.kontakt.telefon, self.kontakt.email], datas)  # Should check only telephone and email.
		self.assertListEqual([True, True], oks)


if __name__ == '__main__':
	unittest.main()
