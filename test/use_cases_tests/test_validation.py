import unittest
from unittest.mock import Mock

from app import APP
from core.domain.arhitektura_kluba import Kontakt
from core.services.email_service import EmailService
from core.services.sms_service import SmsService
from core.use_cases.validation_cases import Validate_kontakt


class test_validate(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=True)

		# MOCKS
		cls.kontakt: Kontakt = Mock()
		cls.kontakt.email = ['jar.fmf@gmail.com']
		cls.kontakt.telefon = ['051240885']

		cls.email_service = Mock(EmailService)
		cls.email_service.obstaja().return_value = True
		cls.sms_service: SmsService = Mock(SmsService)
		cls.sms_service.obstaja().return_value = True

		# USE CASE
		cls.validate_kontakt = Validate_kontakt(emailService=cls.email_service, smsService=cls.sms_service)

	def test_validate_kontakt(self):
		validations = self.validate_kontakt.invoke(self.kontakt)
		oks = [val.ok for val in validations]
		datas = [val.data for val in validations]
		self.assertListEqual(self.kontakt.telefon + self.kontakt.email, datas)  # Should check only telephone and email.
		self.assertListEqual([self.sms_service.obstaja(), self.email_service.obstaja()], oks)


if __name__ == '__main__':
	unittest.main()
