import re
import unittest
from copy import copy
from unittest.mock import MagicMock, call, AsyncMock, ANY

from app import APP, CONST
from core.domain.arhitektura_kluba import Kontakt, TipValidacije, TipKontakta, Oseba
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.use_cases.msg_cases import Msg_send
from core.use_cases.validation_cases import Validate_kontakts_ownerships


class test_kontakts_existances(unittest.TestCase):
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
		APP.init(seed=False)
		cls.case = APP.useCases.validate_kontakts_existances(
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


class test_kontakts_ownerships(unittest.IsolatedAsyncioTestCase):
	oseba = None
	kontakts = None
	msg_send = None
	case = None

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)

		cls.kontakts = [
			Kontakt(data='phone0', tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN),
			Kontakt(data='phone1', tip=TipKontakta.PHONE, validacija=TipValidacije.VALIDIRAN),
			Kontakt(data='phone2', tip=TipKontakta.PHONE, validacija=TipValidacije.POTRJEN),
			Kontakt(data='email0', tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN),
			Kontakt(data='email1', tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN),
			Kontakt(data='email2', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)]

		cls.oseba = Oseba(ime='ime', priimek='priimek', rojen=None, kontakti=cls.kontakts)

		cls.msg_send: Msg_send = AsyncMock(Msg_send)
		cls.msg_send.invoke = AsyncMock()
		cls.case: Validate_kontakts_ownerships = APP.useCases.validate_kontakts_ownerships(msg_send=cls.msg_send)

	def decode_tokens(self, *tokens):
		d = []
		for t in tokens:
			d.append(self.case.auth_verification_token.auth.decode(t).u)
		return d

	async def test_pass(self):
		await self.case.invoke(self.oseba)

		self.assertEqual(len(self.msg_send.invoke.call_args_list), 2)
		self.assertEqual(self.msg_send.invoke.call_args_list, [
			call(kontakt=self.kontakts[1], naslov=None, vsebina=ANY),
			call(kontakt=self.kontakts[-2], naslov=CONST.email_subject.verifikacija, vsebina=ANY)])

		phone_vsebina = self.msg_send.invoke.call_args_list[0].kwargs['vsebina']
		self.assertCountEqual([self.kontakts[1].data], self.decode_tokens(*re.findall(f'{CONST.auth_report_url}/(.*)', phone_vsebina)))
		self.assertCountEqual([self.kontakts[1].data], self.decode_tokens(*re.findall(f'{CONST.auth_confirm_url}/(.*)', phone_vsebina)))

		email_vsebina = self.msg_send.invoke.call_args_list[1].kwargs['vsebina']
		self.assertCountEqual([self.kontakts[-2].data], self.decode_tokens(*re.findall(f'{CONST.auth_report_url}/(.*)\"+', email_vsebina)))
		self.assertCountEqual([self.kontakts[-2].data], self.decode_tokens(*re.findall(f'{CONST.auth_confirm_url}/(.*)\"+', email_vsebina)))


if __name__ == '__main__':
	unittest.main()
