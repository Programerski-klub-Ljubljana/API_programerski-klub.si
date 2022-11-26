import unittest
from copy import copy
from unittest.mock import MagicMock

from core.domain.arhitektura_kluba import Kontakt, TipValidacije, TipKontakta
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.use_cases.validation_cases import Validate_kontakt


class test_kontakt(unittest.TestCase):
	case = None

	@classmethod
	def setUpClass(cls) -> None:
		cls.in_kontakti = [
			Kontakt(data='data0', tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN),
			Kontakt(data='data1', tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN),
			Kontakt(data='data2', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN),
			Kontakt(data='data3', tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN),
			Kontakt(data='data4', tip=TipKontakta.PHONE, validacija=TipValidacije.VALIDIRAN),
			Kontakt(data='data5', tip=TipKontakta.PHONE, validacija=TipValidacije.POTRJEN)]

		cls.case = Validate_kontakt(
			email=MagicMock(EmailService),
			phone=MagicMock(PhoneService))

	def test_all_pass(self):
		self.case.phone.obstaja.return_value = True
		self.case.email.obstaja.return_value = True

		out_kontakti = self.case.invoke(*copy(self.in_kontakti))

		self.assertEqual(out_kontakti, [self.in_kontakti[0], self.in_kontakti[3]])
		self.assertEqual(out_kontakti[0].validacija, TipValidacije.VALIDIRAN)
		self.assertEqual(out_kontakti[1].validacija, TipValidacije.VALIDIRAN)

	def test_all_fail(self):
		self.case.phone.obstaja.return_value = False
		self.case.email.obstaja.return_value = False

		out_kontakti = self.case.invoke(*copy(self.in_kontakti))

		self.assertEqual(out_kontakti, [self.in_kontakti[0], self.in_kontakti[3]])
		self.assertEqual(out_kontakti[0].validacija, TipValidacije.NI_VALIDIRAN)
		self.assertEqual(out_kontakti[1].validacija, TipValidacije.NI_VALIDIRAN)


if __name__ == '__main__':
	unittest.main()
