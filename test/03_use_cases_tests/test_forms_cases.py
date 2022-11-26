import re
import unittest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, call, ANY

from app import APP, CONST
from core.domain.arhitektura_kluba import TipKontakta, TipValidacije, TipOsebe, Kontakt, Oseba
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.use_cases.forms_vpis import StatusVpisa, RazlogDuplikacije, TipProblema


class Test_vpis_status(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.status = StatusVpisa(
			clan=Oseba(ime='ime', priimek='priimek', rojen=None),
			skrbnik=Oseba(ime='ime_skrbnika', priimek='priimek_skrbnika', rojen=None),
			razlogi_duplikacije_skrbnika=[RazlogDuplikacije.SKRBNIK_POSTAJA_CLAN, RazlogDuplikacije.ZE_VPISAN],
			razlogi_duplikacije_clana=[RazlogDuplikacije.CLAN_POSTAJA_SKRBNIK, RazlogDuplikacije.ZE_IMA_VAROVANCA],
			razlogi_prekinitve=[TipProblema.NAPAKE, TipProblema.HACKER, TipProblema.CHUCK_NORIS],
			validirani_podatki_clana=[
				Kontakt(data='data_clan_0', tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN),
				Kontakt(data='data_clan_1', tip=TipKontakta.PHONE, validacija=TipValidacije.VALIDIRAN),
				Kontakt(data='data_clan_2', tip=TipKontakta.PHONE, validacija=TipValidacije.POTRJEN),
			],
			validirani_podatki_skrbnika=[
				Kontakt(data='data_skrbnik_0', tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN),
				Kontakt(data='data_skrbnik_1', tip=TipKontakta.PHONE, validacija=TipValidacije.VALIDIRAN),
				Kontakt(data='data_skrbnik_2', tip=TipKontakta.PHONE, validacija=TipValidacije.POTRJEN),
			]
		)

	def test_napacni_podatki_clana(self):
		kontakti = self.status.napacni_podatki_clana
		self.assertEqual(len(kontakti), 1)
		self.assertEqual(kontakti[0].data, 'data_clan_0')

	def test_napacni_podatki_skrbnika(self):
		kontakti = self.status.napacni_podatki_skrbnika
		self.assertEqual(len(kontakti), 1)
		self.assertEqual(kontakti[0].data, 'data_skrbnik_0')

	def test_stevilo_napacnih_podatkov(self):
		self.assertEqual(self.status.stevilo_napacnih_podatkov, 2)

	def test_validirani_podatki(self):
		kontakti = self.status.validirani_podatki
		self.assertEqual(len(kontakti), 6)
		for i in range(3):
			self.assertEqual(kontakti[i].data, f'data_skrbnik_{i}')
		for i in range(3):
			self.assertEqual(kontakti[i + 3].data, f'data_clan_{i}')

	def test_stevilo_problemov(self):
		self.assertEqual(self.status.stevilo_problemov, 3)

	def test_str(self):
		self.assertEqual(str(self.status), f"""
			Clan   : imepriimek_
			Skrbnik: ime_skrbnikapriimek_skrbnika_
			Razlogi duplikacije skrbnika: [<RazlogDuplikacije.SKRBNIK_POSTAJA_CLAN: '4'>, <RazlogDuplikacije.ZE_VPISAN: '2'>]
			Razlogi duplikacije clana   : [<RazlogDuplikacije.CLAN_POSTAJA_SKRBNIK: '1'>, <RazlogDuplikacije.ZE_IMA_VAROVANCA: '5'>]
			Razlogi prekinitve          : [<TipProblema.NAPAKE: '1'>, <TipProblema.HACKER: '3'>, <TipProblema.CHUCK_NORIS: '2'>]
			Napake skrbnika: data_skrbnik_0
			Napake clana   : data_clan_0
		""".removeprefix('\t\t'))


class Test_forms_vpis(unittest.IsolatedAsyncioTestCase):
	phone_service = None
	email_service = None

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)

		cls.email_service: EmailService = MagicMock(EmailService)
		cls.email_service.send = AsyncMock()

		cls.phone_service: PhoneService = MagicMock(PhoneService)
		cls.phone_service.format = APP.services.phone().format

		validate_kontakt = APP.useCases.validate_kontakt(
			email=cls.email_service,
			phone=cls.phone_service)

		cls.case = APP.useCases.forms_vpis(
			email=cls.email_service,
			phone=cls.phone_service,
			template=APP.services.template(),
			validate_kontakt=validate_kontakt)

	def full_props(self, status):
		prop = []
		for k, v in status.__dict__.items():
			if isinstance(v, list) and len(v) > 0:
				prop.append(k)
			elif isinstance(v, Oseba) and v is not None:
				prop.append(k)
		return prop

	async def test_polnoleten_not_exists_yet_all_pass(self):
		self.email_service.obstaja.return_value = True
		self.phone_service.obstaja.return_value = True

		before_now = datetime.utcnow()
		status: StatusVpisa = await self.case.invoke(
			ime='ime', priimek='priimek',
			dan_rojstva=15, mesec_rojstva=6, leto_rojstva=1234,
			email='mail@gmail.com', telefon='051240885')
		after_now = datetime.utcnow()

		# TEST STATUS ======================================================
		self.assertIsInstance(status, StatusVpisa)
		self.assertListEqual(self.full_props(status), ['clan', 'validirani_podatki_clana'])

		# VALIDIRANI PODATKI CLANA =========================================
		self.assertEqual(status.validirani_podatki_clana, [
			Kontakt(data='mail@gmail.com', tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN),
			Kontakt(data='+38651240885', tip=TipKontakta.PHONE, validacija=TipValidacije.VALIDIRAN)])

		# CLAN =============================================================
		c = status.clan
		self.assertEqual(c.ime, 'ime')
		self.assertEqual(c.priimek, 'priimek')
		self.assertEqual(c.geslo, None)
		self.assertEqual(c.rojen.year, 1234)
		self.assertEqual(c.rojen.month, 6)
		self.assertEqual(c.rojen.day, 15)
		self.assertEqual(len(c.kontakti), 2)
		self.assertEqual(len(c.vpisi), 1)
		self.assertEqual(len(c.izpisi), 0)
		self.assertEqual(c.tip_osebe, [TipOsebe.CLAN])

		# KONTAKTI CLANA ====================================================
		self.assertEqual(c.kontakti[0].data, 'mail@gmail.com')
		self.assertEqual(c.kontakti[0].tip, TipKontakta.EMAIL)
		self.assertEqual(c.kontakti[0].validacija, TipValidacije.VALIDIRAN)

		self.assertEqual(c.kontakti[1].data, '+38651240885')
		self.assertEqual(c.kontakti[1].tip, TipKontakta.PHONE)
		self.assertEqual(c.kontakti[1].validacija, TipValidacije.VALIDIRAN)
		self.assertTrue(before_now <= c.vpisi[0] <= after_now)

		# DB TESTING ========================================================
		with self.case.db.transaction() as root:
			self.assertEqual(len(root.oseba), 1)
			self.assertEqual(root.oseba[0], c)

		# SMS EMAIL TESTING =====================================================
		self.assertEqual(self.case.email.send.call_args_list, [
			call(recipients=['mail@gmail.com'], subject=CONST.email_subject.vpis, vsebina=ANY)])
		self.assertEqual(self.case.phone.sms.call_args_list, [
			call(phone='+38651240885', text=ANY)])

		# TESTING SMS, EMAIL VSEBINA ============================================
		self.assertRegex(self.case.email.send.call_args_list[0].kwargs['vsebina'], r'<a href=".{170,}">')
		self.assertRegex(self.case.phone.sms.call_args_list[0].kwargs['text'], r'https://programerski-klub.si\/.*')


if __name__ == '__main__':
	unittest.main()
