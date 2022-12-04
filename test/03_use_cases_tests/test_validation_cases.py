import re
import unittest
from copy import copy
from unittest.mock import MagicMock, call, AsyncMock, ANY

from app import APP, CONST
from core.domain.arhitektura_kluba import Kontakt, NivoValidiranosti, TipKontakta, Oseba
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.use_cases.msg_cases import Poslji_sporocilo
from core.use_cases.validation_cases import Poslji_test_ki_preveri_lastnistvo_kontakta, Poslji_test_ki_preveri_zeljo_za_koncno_izclanitev


class test_preveri_obstoj_kontakta(unittest.TestCase):
	case = None

	@classmethod
	def setUpClass(cls) -> None:
		cls.in_kontakti = [
			Kontakt(data='data0', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='data1', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='data2', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN),
			Kontakt(data='data3', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='data4', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='data5', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.POTRJEN)]
		APP.init(seed=False)
		cls.case = APP.cases.preveri_obstoj_kontakta(
			email=MagicMock(EmailService),
			phone=MagicMock(PhoneService))

	def test_vsi_obstajajo(self):
		self.case.phone.check_existance.return_value = True
		self.case.email.check_existance.return_value = True

		out_kontakti = self.case.exe(*copy(self.in_kontakti))

		self.assertEqual(out_kontakti, [self.in_kontakti[0], self.in_kontakti[3]])
		self.assertEqual(out_kontakti[0].nivo_validiranosti, NivoValidiranosti.VALIDIRAN)
		self.assertEqual(out_kontakti[1].nivo_validiranosti, NivoValidiranosti.VALIDIRAN)

	def test_noben_ne_obstaja(self):
		self.case.phone.check_existance.return_value = False
		self.case.email.check_existance.return_value = False

		out_kontakti = self.case.exe(*copy(self.in_kontakti))

		self.assertEqual(out_kontakti, [self.in_kontakti[0], self.in_kontakti[3]])
		self.assertEqual(out_kontakti[0].nivo_validiranosti, NivoValidiranosti.NI_VALIDIRAN)
		self.assertEqual(out_kontakti[1].nivo_validiranosti, NivoValidiranosti.NI_VALIDIRAN)


class test_poslji_test_ki_preveri_lastnistvo_kontakta(unittest.IsolatedAsyncioTestCase):
	oseba = None
	kontakts = None
	msg_send = None
	case = None

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)

		cls.kontakts = [
			Kontakt(data='phone0', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='phone1', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='phone2', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.POTRJEN),
			Kontakt(data='email0', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='email1', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='email2', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)]

		cls.oseba = Oseba(ime='ime', priimek='priimek', rojen=None, kontakti=cls.kontakts)

		cls.msg_send: Poslji_sporocilo = MagicMock(Poslji_sporocilo)
		cls.msg_send.exe = AsyncMock()
		cls.case: Poslji_test_ki_preveri_lastnistvo_kontakta = APP.cases.poslji_test_ki_preveri_lastnistvo_kontakta(msg_send=cls.msg_send)

	def decode_tokens(self, *tokens):
		d = []
		for t in tokens:
			d.append(self.case.auth_verification_token.auth.decode(t).d)
		return d

	async def test_je_poslan(self):
		self.assertCountEqual(await self.case.exe(self.oseba), [self.kontakts[1], self.kontakts[-2]])

		self.assertEqual(len(self.msg_send.exe.call_args_list), 2)
		self.assertEqual(self.msg_send.exe.call_args_list, [
			call(kontakt=self.kontakts[1], naslov=None, vsebina=ANY),
			call(kontakt=self.kontakts[-2], naslov=CONST.email_subject.verifikacija, vsebina=ANY)])

		phone_vsebina = self.msg_send.exe.call_args_list[0].kwargs['vsebina']
		self.assertCountEqual([self.kontakts[1]._id], self.decode_tokens(*re.findall(f'{CONST.auth_report_url}/(.*)', phone_vsebina)))
		self.assertCountEqual([self.kontakts[1]._id], self.decode_tokens(*re.findall(f'{CONST.auth_ownership_url}/(.*)', phone_vsebina)))

		email_vsebina = self.msg_send.exe.call_args_list[1].kwargs['vsebina']
		self.assertCountEqual([self.kontakts[-2]._id], self.decode_tokens(*re.findall(f'{CONST.auth_report_url}/(.*)\"+', email_vsebina)))
		self.assertCountEqual([self.kontakts[-2]._id], self.decode_tokens(*re.findall(f'{CONST.auth_ownership_url}/(.*)\"+', email_vsebina)))


class test_poslji_test_ki_preveri_zeljo_za_koncno_izclanitev(unittest.IsolatedAsyncioTestCase):
	auth_verification_token = None
	msg_send = None

	def setUp(cls) -> None:
		APP.init(seed=False)

		cls.oseba = Oseba(ime='ime', priimek='priimek', rojen=None, kontakti=[
			Kontakt(data='data0', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='data1', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='data2', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN),
			Kontakt(data='data3', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='data4', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='data5', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.POTRJEN),
		])
		cls.fail_oseba = Oseba(ime='ime', priimek='priimek', rojen=None, kontakti=[
			Kontakt(data='data0', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='data1', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='data3', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='data4', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
		])

		cls.msg_send: Poslji_sporocilo = MagicMock(Poslji_sporocilo)
		cls.msg_send.exe = AsyncMock()

		cls.case: Poslji_test_ki_preveri_zeljo_za_koncno_izclanitev = APP.cases.poslji_test_ki_preveri_zeljo_za_koncno_izclanitev(msg_send=cls.msg_send)

	def decode_tokens(self, *tokens):
		d = []
		for t in tokens:
			d.append(self.case.auth_verification_token.auth.decode(t).d)
		return d

	async def test_je_poslan(self):
		self.assertEqual(await self.case.exe(self.oseba), self.oseba.kontakti[2])

		self.assertEqual(self.msg_send.exe.call_args_list, [
			call(kontakt=self.oseba.kontakti[2], naslov=CONST.email_subject.verifikacija_izpisa, vsebina=ANY)])

		email_vsebina = self.msg_send.exe.call_args_list[0].kwargs['vsebina']
		self.assertCountEqual([self.oseba._id], self.decode_tokens(*re.findall(f'{CONST.auth_report_url}/(.*)\"+', email_vsebina)))
		self.assertCountEqual([self.oseba._id], self.decode_tokens(*re.findall(f'{CONST.auth_signout_url}/(.*)\"+', email_vsebina)))

	async def test_ni_poslan(self):
		self.assertFalse(await self.case.exe(self.fail_oseba))
		self.assertEqual(self.msg_send.exe.call_args_list, [])


if __name__ == '__main__':
	unittest.main()
