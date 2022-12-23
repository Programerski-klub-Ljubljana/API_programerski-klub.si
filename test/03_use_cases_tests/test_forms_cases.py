import unittest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, call, AsyncMock

from app import APP, CONST
from core.domain.arhitektura_kluba import TipKontakta, NivoValidiranosti, TipOsebe, Kontakt, Oseba
from core.services.phone_service import PhoneService
from core.use_cases.validation_cases import Preveri_obstoj_kontakta, Poslji_test_ki_preveri_lastnistvo_kontakta, \
	Poslji_test_ki_preveri_zeljo_za_koncno_izclanitev
from core.use_cases.zacni_izclanitveni_postopek import Zacni_izclanitveni_postopek, StatusIzpisa, TipPrekinitveIzpisa
from core.use_cases.zacni_vclanitveni_postopek import StatusVpisa, TipPrekinitveVpisa


class Test_status_vpisa(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.status = StatusVpisa(
			clan=Oseba(ime='ime', priimek='priimek', rojen=None),
			skrbnik=Oseba(ime='ime_skrbnika', priimek='priimek_skrbnika', rojen=None),
			razlogi_prekinitve=[TipPrekinitveVpisa.NAPAKE, TipPrekinitveVpisa.HACKER, TipPrekinitveVpisa.CHUCK_NORIS],
			validirani_podatki_clana=[
				Kontakt(data='data_clan_0', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
				Kontakt(data='data_clan_1', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
				Kontakt(data='data_clan_2', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.POTRJEN),
			],
			validirani_podatki_skrbnika=[
				Kontakt(data='data_skrbnik_0', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
				Kontakt(data='data_skrbnik_1', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
				Kontakt(data='data_skrbnik_2', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.POTRJEN),
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
			Razlogi prekinitve          : [<TipPrekinitveVpisa.NAPAKE: '2'>, <TipPrekinitveVpisa.HACKER: '4'>, <TipPrekinitveVpisa.CHUCK_NORIS: '3'>]
			Napake skrbnika: data_skrbnik_0
			Napake clana   : data_clan_0
		""".removeprefix('\t\t'))


class Test_zacni_vclanitveni_postopek(unittest.IsolatedAsyncioTestCase):
	phone_service = None
	validate_kontakts_ownerships = None
	validate_kontakts_existances = None

	def setUp(self) -> None:
		APP.init(seed=False)

		# MOCKS
		self.phone_service: PhoneService = MagicMock(PhoneService, name='PhoneService')
		self.validate_kontakts_existances = MagicMock(Preveri_obstoj_kontakta, name='Validate_kontakts_existances')
		self.validate_kontakts_ownerships = AsyncMock(Poslji_test_ki_preveri_lastnistvo_kontakta, name='Validate_kontakts_ownerships')
		self.validate_kontakts_ownerships.exe = AsyncMock()

		# MOCKS LOGIC
		self.phone_service.format.side_effect = lambda phone: phone
		self.phone_service.origin.side_effect = APP.services.phone().origin

		# SETUP
		self.case = APP.cases.zacni_vclanitveni_postopek(
			phone=self.phone_service,
			validate_kontakts_existances=self.validate_kontakts_existances,
			validate_kontakts_ownerships=self.validate_kontakts_ownerships)

		self.merge_call_args = []
		self.db_find_and_merge: bool = False

		def find(entity: Oseba):
			if self.db_find_and_merge:
				self.merge_call_args.append(entity)
				yield entity

		self.case.db.find = find

		self.today = date.today()

		self.skrbnik = Oseba(ime='ime_skrbnika', priimek='priimek_skrbnika', rojen=None, kontakti=[
			Kontakt(data=CONST.alt_email, tip=TipKontakta.EMAIL), Kontakt(data='phone_skrbnika0', tip=TipKontakta.PHONE)])

		self.polnoletna_oseba = Oseba(ime='ime', priimek='priimek', rojen=date(year=self.today.year - 20, month=1, day=1), kontakti=[
			Kontakt(data=CONST.email, tip=TipKontakta.EMAIL), Kontakt(data=CONST.phone, tip=TipKontakta.PHONE)])

		self.mladoletna_oseba = Oseba(ime='ime', priimek='priimek', rojen=date(year=self.today.year - 10, month=1, day=1), kontakti=[
			Kontakt(data=CONST.email, tip=TipKontakta.EMAIL), Kontakt(data=CONST.phone, tip=TipKontakta.PHONE)])

		# DB
		with self.case.db.transaction() as root:
			root.oseba.clear()
			assert len(root.oseba) == 0

	def assertEqualProperties(self, status: StatusVpisa, expected):
		prop = []
		for k, v in status.__dict__.items():
			if isinstance(v, list) and len(v) > 0:
				prop.append(k)
			elif isinstance(v, Oseba | MagicMock) and v is not None:
				prop.append(k)

		self.assertCountEqual(sorted(prop), sorted(expected))

	def assertEqualOseba(self, original_oseba, status_oseba, vpis: bool = False, tip: TipOsebe = TipOsebe.CLAN):
		# MORA IMETI VPIS.
		if vpis:
			before = datetime.now()
			self.assertAlmostEqual(before.timestamp(), status_oseba.vpisi[0].timestamp(), places=-1)
			self.assertEqual(len(status_oseba.vpisi), 1)

		# MORA IMETI ENAKE INFORMACIJE
		self.assertEqual(original_oseba.ime, status_oseba.ime)
		self.assertEqual(original_oseba.priimek, status_oseba.priimek)
		self.assertEqual(original_oseba.rojen, status_oseba.rojen)

		# MORA BITI PRAVEGA TIPA
		self.assertEqual(status_oseba.tip_osebe, [tip])

		# NESME IMETI IZPISOV
		self.assertEqual(original_oseba.izpisi, [])

		# NESPREMENJENO STEVILO KONTAKTOV (BREZ MERGA)
		self.assertEqual(len(original_oseba.kontakti), len(status_oseba.kontakti))

		# ENAKO STEVILO KONTAKTOV
		for i, k1 in enumerate(original_oseba.kontakti):
			k2 = status_oseba.kontakti[i]

			# ENAKE INFORMACIJE V KONTAKTIH
			self.assertEqual(k1.tip, k2.tip)
			self.assertEqual(k1.data, k2.data)

	async def exe(self, clan: Oseba, skrbnik: Oseba = None, db_saved: bool = True):
		kwargs = {
			'ime': clan.ime,
			'priimek': clan.priimek,
			'email': clan.kontakti[0].data,
			'telefon': clan.kontakti[1].data,
			'dan_rojstva': clan.rojen.day,
			'mesec_rojstva': clan.rojen.month,
			'leto_rojstva': clan.rojen.year,
		}

		if skrbnik is not None:
			kwargs = {
				**kwargs, 'ime_skrbnika': skrbnik.ime, 'priimek_skrbnika': skrbnik.priimek,
				'email_skrbnika': skrbnik.kontakti[0].data, 'telefon_skrbnika': skrbnik.kontakti[1].data}

		# INVOKE
		before = datetime.now() - timedelta(seconds=1)
		status: StatusVpisa = await self.case.exe(**kwargs)
		after = datetime.now() + timedelta(seconds=1)

		# PREVERI ALI SE JE FORMATIRANJE TELEFONA ZGODILO
		phone_format_call_args_list = [call(phone=clan.kontakti[1].data)]
		if skrbnik is not None:
			phone_format_call_args_list.append(call(phone=skrbnik.kontakti[1].data))
		self.assertCountEqual(self.phone_service.format.call_args_list, phone_format_call_args_list)

		# PREVERI ALI JE CLAN V VPISNEM STATUSU
		# PREVERI CE SO PROPERTIJI CLANA VSI COOL
		self.assertEqualOseba(original_oseba=clan, status_oseba=status.clan, vpis=True, tip=TipOsebe.CLAN)

		# PREVERI ALI SE JE MERGE ZGODIL...
		if self.db_find_and_merge:
			merge_call_args_list = [status.clan]
			if skrbnik is not None:
				merge_call_args_list.append(status.skrbnik)
			self.assertCountEqual(self.merge_call_args, merge_call_args_list)

		# PREVERI ALI JE SKRBNIK V VPISNEM STATUSU
		# PREVERI CE SO PROPERTIJI SKRBNIKA VSI COOL
		if skrbnik is not None:
			self.assertEqualOseba(original_oseba=skrbnik, status_oseba=status.skrbnik, vpis=False, tip=TipOsebe.SKRBNIK)

		# ALI SE JE VALIDACIJA PODATKOV ZGODILA
		validate_kontakts_existances_call_args_list = [call(*status.clan.kontakti)]
		if skrbnik is not None:
			validate_kontakts_existances_call_args_list.append(call(*status.skrbnik.kontakti))
		self.assertEqual(self.validate_kontakts_existances.exe.call_args_list, validate_kontakts_existances_call_args_list)

		# PREVERI ALI IMA STATUS VRACAJOCE PODATKE OD PRAVILNEGA SERVISA
		self.assertEqual(status.validirani_podatki_clana, self.validate_kontakts_existances.exe())
		if skrbnik is not None:
			self.assertEqual(status.validirani_podatki_skrbnika, self.validate_kontakts_existances.exe())

		# PREVERI CE SO SE STVARI PRAVILNO SHRANILE IN POVEZALE MED SABO V DB-ju
		with self.case.db.transaction() as root:
			if db_saved:
				self.assertEqual(len(root.oseba), 1 if skrbnik is None else 2)
				self.assertEqual(root.oseba[0], status.clan)
				if skrbnik is not None:
					self.assertEqual(root.oseba[1], status.skrbnik)
					self.assertEqual(root.oseba[0]._connections, [status.skrbnik])
					self.assertEqual(root.oseba[1]._connections, [status.clan])
			else:
				self.assertEqual(len(root.oseba), 0)

		# PREVERI ALI SE JE CUSTOMER V PAYMENT DODAL IN AKTIVIRAL SUBSCRIPTION NA NJEMU.
		customer = self.case.payment.get_customer(id=status.clan._id)
		if db_saved:
			c = status.clan
			s = status.skrbnik
			self.assertEqual(customer.id, c._id)
			self.assertEqual(customer.name, f'{c.ime} {c.priimek}')
			self.assertEqual(customer.billing_email, [k.data for k in (s.kontakti if c.mladoletnik else c.kontakti) if k.tip == TipKontakta.EMAIL][0])
			self.assertEqual(customer.description, None)
			self.assertEqual(customer.balance, 0)
			self.assertEqual(customer.discount, None)
			self.assertEqual(customer.delinquent, False)
			self.assertTrue(before < customer.created < after, f'{before} {customer.created} {after}')
			self.assertEqual(customer.languages, ['sl'])
			self.assertEqual(customer.deleted, False)
		else:
			self.assertIsNone(customer, msg=customer)

		# PREVERI ALI SO SE PRAVILNE FUNKCIJE KLICALE KI PREVERIJO KONTAKTS OWNERSHIPS
		validate_ownerships_call_args_list = [call(oseba=status.clan)]
		if skrbnik is not None:
			validate_ownerships_call_args_list.append(call(oseba=status.skrbnik))
		self.assertCountEqual(self.validate_kontakts_ownerships.exe.call_args_list, validate_ownerships_call_args_list if db_saved else [])

		return status

	async def test_polnoletnik_se_vclani(self):
		status = await self.exe(self.polnoletna_oseba, db_saved=True)
		self.assertEqualProperties(status, ['clan', 'validirani_podatki_clana'])

	async def test_polnoletnik_vnese_napacne_podatke(self):
		self.polnoletna_oseba.kontakti[0].nivo_validiranosti = NivoValidiranosti.VALIDIRAN
		self.validate_kontakts_existances.exe.side_effect = lambda *kontakti: self.polnoletna_oseba.kontakti

		status = await self.exe(self.polnoletna_oseba, db_saved=False)
		self.assertEqualProperties(status, ['clan', 'validirani_podatki_clana', 'razlogi_prekinitve'])
		self.assertCountEqual(status.razlogi_prekinitve, [TipPrekinitveVpisa.NAPAKE])

	async def test_polnoletnik_je_hacker(self):
		self.validate_kontakts_existances.exe.side_effect = lambda *kontakti: self.polnoletna_oseba.kontakti

		status = await self.exe(self.polnoletna_oseba, db_saved=False)
		self.assertEqualProperties(status, ['clan', 'validirani_podatki_clana', 'razlogi_prekinitve'])
		self.assertCountEqual(status.razlogi_prekinitve, [TipPrekinitveVpisa.NAPAKE, TipPrekinitveVpisa.HACKER])

	async def test_polnoletnik_je_ze_vpisan(self):
		self.db_find_and_merge = True
		status = await self.exe(self.polnoletna_oseba, db_saved=False)
		self.assertEqualProperties(status, ['clan', 'validirani_podatki_clana', 'razlogi_prekinitve'])
		self.assertCountEqual(status.razlogi_prekinitve, [TipPrekinitveVpisa.ZE_VPISAN])

	async def test_mladoletnik_se_vclani(self):
		status = await self.exe(self.mladoletna_oseba, self.skrbnik, db_saved=True)
		self.assertEqualProperties(status, ['skrbnik', 'clan', 'validirani_podatki_clana', 'validirani_podatki_skrbnika'])

	async def test_mladoletnik_je_chuck_noris(self):
		self.mladoletna_oseba.kontakti[0].data = self.skrbnik.kontakti[0].data
		status = await self.exe(self.mladoletna_oseba, self.skrbnik, db_saved=False)
		self.assertEqualProperties(status, ['skrbnik', 'clan', 'validirani_podatki_clana', 'validirani_podatki_skrbnika', 'razlogi_prekinitve'])
		self.assertCountEqual(status.razlogi_prekinitve, [TipPrekinitveVpisa.CHUCK_NORIS])

	async def test_mladoletnik_vnese_napacne_podatke(self):
		self.mladoletna_oseba.kontakti[0].nivo_validiranosti = NivoValidiranosti.VALIDIRAN
		self.validate_kontakts_existances.exe.side_effect = lambda *kontakti: self.mladoletna_oseba.kontakti + self.skrbnik.kontakti

		status = await self.exe(self.mladoletna_oseba, self.skrbnik, db_saved=False)
		self.assertEqualProperties(status, ['skrbnik', 'clan', 'validirani_podatki_clana', 'validirani_podatki_skrbnika', 'razlogi_prekinitve'])
		self.assertCountEqual(status.razlogi_prekinitve, [TipPrekinitveVpisa.NAPAKE])

	async def test_mladoletnik_je_hacker(self):
		self.validate_kontakts_existances.exe.side_effect = lambda *kontakti: self.mladoletna_oseba.kontakti + self.skrbnik.kontakti
		self.mladoletna_oseba.kontakti[0].data = self.skrbnik.kontakti[0].data

		status = await self.exe(self.mladoletna_oseba, self.skrbnik, db_saved=False)
		self.assertEqualProperties(status, ['skrbnik', 'clan', 'validirani_podatki_clana', 'validirani_podatki_skrbnika', 'razlogi_prekinitve'])
		self.assertCountEqual(status.razlogi_prekinitve, [TipPrekinitveVpisa.CHUCK_NORIS, TipPrekinitveVpisa.NAPAKE, TipPrekinitveVpisa.HACKER])

	async def test_mladoletnik_je_ze_vpisan(self):
		self.db_find_and_merge = True
		status = await self.exe(self.mladoletna_oseba, self.skrbnik, db_saved=False)
		self.assertEqualProperties(status, ['skrbnik', 'clan', 'validirani_podatki_clana', 'validirani_podatki_skrbnika', 'razlogi_prekinitve'])
		self.assertCountEqual(status.razlogi_prekinitve, [TipPrekinitveVpisa.ZE_VPISAN])


class Test_zacni_izclanitveni_postopek(unittest.IsolatedAsyncioTestCase):
	def setUp(self) -> None:
		APP.init(seed=False)

		# SETUP
		self.validate_izpis_request = MagicMock(Poslji_test_ki_preveri_zeljo_za_koncno_izclanitev)
		self.validate_izpis_request.exe = AsyncMock()
		self.case: Zacni_izclanitveni_postopek = APP.cases.zacni_izclanitveni_postopek(validate_izpis_request=self.validate_izpis_request)
		self.oseba = Oseba(ime='ime', priimek='priimek', rojen=None, kontakti=[
			Kontakt(data='data', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)])
		self.vpisana_oseba = Oseba(ime='ime2', priimek='priimek2', rojen=None, kontakti=[
			Kontakt(data='data2', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)])
		self.vpisana_oseba.nov_vpis()

		with self.case.db.transaction() as root:
			root.oseba.clear()
			root.save(self.oseba, self.vpisana_oseba)

	def tearDown(self) -> None:
		with self.case.db.transaction() as root:
			root.oseba.clear()

	async def test_izclanitev(self):
		status: StatusIzpisa = await self.case.exe(
			ime=self.vpisana_oseba.ime, priimek=self.vpisana_oseba.priimek, email=self.vpisana_oseba.kontakti[0].data, razlog='razlog')

		self.assertEqual(status.clan, self.vpisana_oseba)
		self.assertEqual(status.razlogi_prekinitve, [])
		self.assertEqual(self.validate_izpis_request.exe.call_args_list, [
			call(oseba=self.vpisana_oseba)
		])

	async def test_ni_vpisan(self):
		status: StatusIzpisa = await self.case.exe(
			ime=self.oseba.ime, priimek=self.oseba.priimek, email=self.oseba.kontakti[0].data, razlog='razlog')

		self.assertEqual(status.clan, self.oseba)
		self.assertEqual(status.razlogi_prekinitve, [TipPrekinitveIzpisa.NI_VPISAN])
		self.assertEqual(self.validate_izpis_request.exe.call_args_list, [])

	async def test_ne_obstaja(self):
		status: StatusIzpisa = await self.case.exe(
			ime=self.oseba.ime, priimek=self.oseba.priimek, email='xxx', razlog='razlog')

		self.assertEqual(status.clan, None)
		self.assertEqual(status.razlogi_prekinitve, [TipPrekinitveIzpisa.NE_OBSTAJA])
		self.assertEqual(self.validate_izpis_request.exe.call_args_list, [])


if __name__ == '__main__':
	unittest.main()
