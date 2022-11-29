import re
import unittest
from datetime import datetime
from unittest.mock import MagicMock, call, ANY

from app import APP, CONST
from core.domain.arhitektura_kluba import TipKontakta, TipValidacije, TipOsebe, Kontakt, Oseba
from core.services.db_service import DbService, DbRoot
from core.services.phone_service import PhoneService
from core.use_cases.db_cases import Db_merge_oseba
from core.use_cases.forms_vpis import StatusVpisa, TipProblema
from core.use_cases.validation_cases import Validate_kontakts_existances, Validate_kontakts_ownerships


class Test_vpis_status(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.status = StatusVpisa(
			clan=Oseba(ime='ime', priimek='priimek', rojen=None),
			skrbnik=Oseba(ime='ime_skrbnika', priimek='priimek_skrbnika', rojen=None),
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
			Razlogi prekinitve          : [<TipProblema.NAPAKE: '1'>, <TipProblema.HACKER: '3'>, <TipProblema.CHUCK_NORIS: '2'>]
			Napake skrbnika: data_skrbnik_0
			Napake clana   : data_clan_0
		""".removeprefix('\t\t'))


class AsyncMock(MagicMock):
	async def __call__(self, *args, **kwargs):
		return super(AsyncMock, self).__call__(*args, **kwargs)

	def __enter__(self):
		return self


class Test_forms_vpis(unittest.IsolatedAsyncioTestCase):
	db_service = None
	phone_service = None
	validate_kontakts_ownerships = None
	validate_kontakts_existances = None
	db_merge_oseba = None

	def setUp(self) -> None:
		APP.init(seed=False)

		# MOCKS
		self.root = MagicMock(DbRoot, name='DbRoot')
		self.db_service: DbService = MagicMock(DbService, name='DbService')
		self.phone_service: PhoneService = MagicMock(PhoneService, name='PhoneService')
		self.validate_kontakts_existances = MagicMock(Validate_kontakts_existances, name='Validate_kontakts_existances')
		self.validate_kontakts_ownerships = AsyncMock(Validate_kontakts_ownerships, name='Validate_kontakts_ownerships')
		self.db_merge_oseba = MagicMock(Db_merge_oseba, name='Db_merge_oseba')

		# SETUP
		self.case = APP.useCases.forms_vpis(
			db=self.db_service,
			phone=self.phone_service,
			validate_kontakts_existances=self.validate_kontakts_existances,
			validate_kontakts_ownerships=self.validate_kontakts_ownerships,
			db_merge_oseba=self.db_merge_oseba)

		# LOGIC
		self.phone_service.format = lambda phone: phone
		self.db_merge_oseba.invoke = lambda oseba, as_type: oseba

	# MOCKS LOGIC
	def full_props(self, status):
		prop = []
		for k, v in status.__dict__.items():
			if isinstance(v, list) and len(v) > 0:
				prop.append(k)
			elif isinstance(v, Oseba | MagicMock) and v is not None:
				prop.append(k)
		return prop

	async def test_polnoleten_all_pass(self):
		leto = datetime.utcnow().year - 20
		# INVOKE
		status: StatusVpisa = await self.case.invoke(
			ime='ime', priimek='priimek',
			email='email', telefon='telefon',
			dan_rojstva=15, mesec_rojstva=6, leto_rojstva=leto,
			ime_skrbnika='ime_skrbnika', priimek_skrbnika='priimek_skrbnika',
			email_skrbnika='email_skrbnika', telefon_skrbnika="telefon_skrbnika")

		# TEST STATUS ======================================================
		self.assertListEqual(self.full_props(status), ['clan', 'validirani_podatki_clana'])

		self.assertEqual(status.clan.ime, 'ime')
		self.assertEqual(status.clan.priimek, 'priimek')
		self.assertEqual(status.clan.rojen, datetime(year=leto, month=6, day=15))
		self.assertTrue(status.clan.has_kontakt_data('email'))
		self.assertTrue(status.clan.has_kontakt_data('phone'))
		self.assertEqual(status.clan.tip_osebe, [TipOsebe.CLAN])
		self.assertEqual(status.clan.izpisi, [])
		self.assertEqual(len(status.clan.vpisi), [])


	async def test_clan_polnoleten_not_exists_yet_all_pass(self):
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
		self.assertEqual(c.tip_osebe, [TipOsebe.CLAN])
		self.assertEqual(len(c.kontakti), 2)
		self.assertEqual(len(c.vpisi), 1)
		self.assertEqual(len(c.izpisi), 0)
		self.assertTrue(before_now <= c.vpisi[0] <= after_now)

		# KONTAKTI CLANA ====================================================
		self.assertEqual(c.kontakti[0].data, 'mail@gmail.com')
		self.assertEqual(c.kontakti[0].tip, TipKontakta.EMAIL)
		self.assertEqual(c.kontakti[0].validacija, TipValidacije.VALIDIRAN)

		self.assertEqual(c.kontakti[1].data, '+38651240885')
		self.assertEqual(c.kontakti[1].tip, TipKontakta.PHONE)
		self.assertEqual(c.kontakti[1].validacija, TipValidacije.VALIDIRAN)

		# DB TESTING ========================================================
		with self.case.db.transaction() as root:
			self.assertEqual(len(root.oseba), 1)
			self.assertEqual(root.oseba[0], c)

		# SMS EMAIL TESTING =====================================================
		self.assertEqual(self.case.email.send.call_args_list, [
			call(recipients=['mail@gmail.com'], subject=CONST.email_subject.vpis, vsebina=ANY)])
		self.assertEqual(self.case.phone.sms.call_args_list, [
			call(phone='+38651240885', text=ANY)])

		# TESTING SMS, EMAIL TOKENS ============================================
		sms = self.case.phone.sms.call_args_list[0].kwargs['text']
		email = self.case.phone.sms.call_args_list[0].kwargs['text']

		tokens = re.findall(r"https://programerski-klub\.si/api/auth/report/(.*)", sms)
		tokens += re.findall(r"https://programerski-klub\.si/api/auth/confirm/(.*)$", sms)
		tokens += re.findall(r"https://programerski-klub\.si/api/auth/report/(.*)$", email)
		tokens += re.findall(r"https://programerski-klub\.si/api/auth/confirm/(.*)$", email)

		for token in tokens:
			self.assertIn(self.case.auth_verification_token.auth.decode(token).u,
			              [k.data for k in c.kontakti])


if __name__ == '__main__':
	unittest.main()
