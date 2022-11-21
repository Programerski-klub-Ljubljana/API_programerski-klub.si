import unittest
from unittest.mock import Mock

from app import APP
from core.domain.arhitektura_kluba import Kontakt, TipKontakta, TipValidacije
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.use_cases.validation_cases import Validate_kontakt


class test_validate(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=True)

		# MOCKS
		cls.kontakt: Kontakt = Mock(Kontakt)
		cls.kontakt.data = 'jar.fmf@gmail.com'
		cls.kontakt.tip = TipKontakta.EMAIL
		cls.kontakt.validacija = TipValidacije.NI_VALIDIRAN
		cls.email_service = Mock(EmailService)
		cls.email_service.obstaja.return_value = TipValidacije.VALIDIRAN
		cls.sms_service: PhoneService = Mock(PhoneService)
		cls.sms_service.obstaja.return_value = TipValidacije.VALIDIRAN

		# USE CASE
		cls.validate_kontakt = Validate_kontakt(email=cls.email_service, phone=cls.sms_service)

	def test_validate_kontakt(self):
		validated_kontakti: list[Kontakt] = self.validate_kontakt.invoke(self.kontakt)
		self.assertEqual(len(validated_kontakti), 1)
		self.assertEqual(validated_kontakti[0].validacija, TipValidacije.VALIDIRAN)


if __name__ == '__main__':
	unittest.main()
