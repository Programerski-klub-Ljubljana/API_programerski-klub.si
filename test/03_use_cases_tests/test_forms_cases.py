import unittest
from datetime import date, datetime
from unittest.mock import MagicMock, call, AsyncMock

from app import APP
from core.domain.arhitektura_kluba import TipKontakta, TipValidacije, TipOsebe, Kontakt, Oseba
from core.services.phone_service import PhoneService
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


class Test_forms_vpis(unittest.IsolatedAsyncioTestCase):
	phone_service = None
	validate_kontakts_ownerships = None
	validate_kontakts_existances = None

	def setUp(self) -> None:
		APP.init(seed=False)

		# MOCKS
		self.phone_service: PhoneService = MagicMock(PhoneService, name='PhoneService')
		self.validate_kontakts_existances = MagicMock(Validate_kontakts_existances, name='Validate_kontakts_existances')
		self.validate_kontakts_ownerships = AsyncMock(Validate_kontakts_ownerships, name='Validate_kontakts_ownerships')
		self.validate_kontakts_ownerships.invoke = AsyncMock()

		# MOCKS LOGIC
		self.phone_service.format.side_effect = lambda phone: phone

		# SETUP
		self.case = APP.useCases.forms_vpis(
			phone=self.phone_service,
			validate_kontakts_existances=self.validate_kontakts_existances,
			validate_kontakts_ownerships=self.validate_kontakts_ownerships)

		self.today = date.today()
		self.skrbnik = Oseba(ime='ime_skrbnika', priimek='priimek_skrbnika', rojen=None, kontakti=[
			Kontakt(data='email_skrbnika0', tip=TipKontakta.EMAIL),
			Kontakt(data='phone_skrbnika0', tip=TipKontakta.PHONE),
		])
		self.skrbnik_confirmed = Oseba(ime='ime_skrbnika', priimek='priimek_skrbnika', rojen=None, kontakti=[
			Kontakt(data='email_skrbnika0', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN),
			Kontakt(data='email_skrbnika0', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)
		])
		self.polnoletna_oseba = Oseba(ime='ime', priimek='priimek', rojen=date(year=self.today.year - 20, month=1, day=1), kontakti=[
			Kontakt(data='email0', tip=TipKontakta.EMAIL),
			Kontakt(data='phone0', tip=TipKontakta.PHONE),
		])
		self.mladoletna_oseba = Oseba(ime='ime', priimek='priimek', rojen=date(year=self.today.year - 10, month=1, day=1), kontakti=[
			Kontakt(data='email0', tip=TipKontakta.EMAIL),
			Kontakt(data='phone0', tip=TipKontakta.PHONE),
		])

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
		if vpis:
			before = datetime.now()
			self.assertAlmostEqual(before.timestamp() / 10000, original_oseba.vpisi[0].timestamp() / 10000, places=0)
			self.assertEqual(len(original_oseba.vpisi), 1)

		self.assertEqual(original_oseba.ime, status_oseba.ime)
		self.assertEqual(original_oseba.priimek, status_oseba.priimek)
		self.assertEqual(original_oseba.rojen, status_oseba.rojen)
		self.assertEqual(original_oseba.tip_osebe, [tip])
		self.assertEqual(original_oseba.izpisi, [])

		self.assertEqual(len(original_oseba.kontakti), len(status_oseba.kontakti))
		for i, k1 in enumerate(original_oseba.kontakti):
			k2 = status_oseba.kontakti[i]
			self.assertEqual(k1.tip, k2.tip)
			self.assertEqual(k1.data, k2.data)

	# MORA SE NAHAJATI V STATUSU
	# MORA IMETI TELEFON FORMATIRAN
	# MORA IMETI KONTAKTE NEVALIDIRANE
	# MORA BITI TIPA CLAN

	# MORA IMETI NOV VPIS
	# TODO: MERGE SE MORA ZGODITI CE ZE OBSTAJA
	# PREVERITI SE MORAJO KONTAKTI CE OBSTAJAJO
	# V PRIMERU NAPAK HACKER ALI NAPAKE
	# V BAZI SE MORA SHRANITI
	# CLAN MORA BITI POVEZAN Z SKRBNIKOM
	# TODO: VALIDIRATI SE MORA KONTAKT OVNERSHIP
	async def invoke(self, clan: Oseba, skrbnik: Oseba = None, db_saved: bool = True, merged: bool = True):
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
		status: StatusVpisa = await self.case.invoke(**kwargs)

		if not merged:
			self.assertEqualOseba(status.clan, clan, vpis=True, tip=TipOsebe.CLAN)
		self.assertEqual(status.validirani_podatki_clana, self.validate_kontakts_existances.invoke())

		db_merge_oseba_calls = [call(oseba=status.clan)]
		validate_ownerships = [call(oseba=status.clan)]

		if skrbnik is not None:
			db_merge_oseba_calls.append(call(oseba=status.skrbnik))
			validate_ownerships.append(call(oseba=status.skrbnik))
			self.assertEqualOseba(status.skrbnik, skrbnik, vpis=False, tip=TipOsebe.SKRBNIK)
			self.assertEqual(status.validirani_podatki_skrbnika, self.validate_kontakts_existances.invoke())

		# DB SAVED
		if not merged:
			with self.case.db.transaction() as root:
				if db_saved:
					self.assertCountEqual(self.validate_kontakts_ownerships.invoke.call_args_list, validate_ownerships)

					self.assertEqual(len(root.oseba), 1 if skrbnik is None else 2)
					self.assertEqual(root.oseba[0], status.clan)
					if skrbnik is not None:
						self.assertEqual(root.oseba[1], status.skrbnik)
						self.assertEqual(root.oseba[0]._povezave, [status.skrbnik])
						self.assertEqual(root.oseba[1]._povezave, [status.clan])
				else:
					self.assertEqual(len(root.oseba), 0)

		return status

	async def test_polnoleten_all_pass(self):
		status = await self.invoke(self.polnoletna_oseba, db_saved=True)
		self.assertEqualProperties(status, ['clan', 'validirani_podatki_clana'])

	async def test_polnoleten_all_pass_merge(self):
		kontakti = [Kontakt(data='old_email0', tip=TipKontakta.EMAIL), Kontakt(data='old_phone0', tip=TipKontakta.PHONE)]
		old_person = Oseba(ime='ime', priimek='priimek', rojen=self.polnoletna_oseba.rojen, tip_osebe=[TipOsebe.SKRBNIK], kontakti=kontakti)

		new_person = self.polnoletna_oseba

		self.assertIsNotNone(new_person.rojen)
		self.assertEqual(len(new_person.kontakti), 2)

		with self.case.db.transaction() as root:
			root.oseba.append(old_person)
			assert len(root.oseba) == 1

		status = await self.invoke(clan=new_person, merged=True)
		self.assertEqualProperties(status, ['clan', 'validirani_podatki_clana'])

		with self.case.db.transaction() as root:
			self.assertEqual(len(root.oseba), 1)
			self.assertEqual(root.oseba[0].rojen, new_person.rojen)
			self.assertCountEqual(root.oseba[0].kontakti, kontakti + self.polnoletna_oseba.kontakti)
			self.assertCountEqual(root.oseba[0].vpisi, self.polnoletna_oseba.vpisi + old_person.vpisi)
			self.assertEqual(root.oseba[0].tip_osebe, [TipOsebe.SKRBNIK, TipOsebe.CLAN])

	async def test_polnoleten_napacni_podatki(self):
		self.polnoletna_oseba.kontakti[0].validacija = TipValidacije.VALIDIRAN
		self.validate_kontakts_existances.invoke.side_effect = lambda *kontakti: self.polnoletna_oseba.kontakti

		status = await self.invoke(self.polnoletna_oseba, db_saved=False)
		self.assertEqualProperties(status, ['clan', 'validirani_podatki_clana', 'razlogi_prekinitve'])
		self.assertCountEqual(status.razlogi_prekinitve, [TipProblema.NAPAKE])

	async def test_polnoleten_hacker(self):
		self.validate_kontakts_existances.invoke.side_effect = lambda *kontakti: self.polnoletna_oseba.kontakti

		status = await self.invoke(self.polnoletna_oseba, db_saved=False)
		self.assertEqualProperties(status, ['clan', 'validirani_podatki_clana', 'razlogi_prekinitve'])
		self.assertCountEqual(status.razlogi_prekinitve, [TipProblema.NAPAKE, TipProblema.HACKER])

	async def test_mladoletnik_all_pass(self):
		status = await self.invoke(self.mladoletna_oseba, self.skrbnik, db_saved=True)
		self.assertEqualProperties(status, ['skrbnik', 'clan', 'validirani_podatki_clana', 'validirani_podatki_skrbnika'])

	async def test_mladoletnik_all_pass_merge(self):
		kontakti_clana = [Kontakt(data='old_email0', tip=TipKontakta.EMAIL), Kontakt(data='old_phone0', tip=TipKontakta.PHONE)]
		kontakti_skrbnika = [Kontakt(data='skrbnik_old_email0', tip=TipKontakta.EMAIL)] + self.skrbnik_confirmed.kontakti
		old_person = Oseba(ime='ime', priimek='priimek', rojen=self.polnoletna_oseba.rojen, tip_osebe=[TipOsebe.SKRBNIK], kontakti=kontakti_clana)
		old_skrbnik = Oseba(
			ime='ime_skrbnika', priimek='priimek_skrbnika', rojen=None, tip_osebe=[TipOsebe.CLAN], kontakti=kontakti_skrbnika)

		new_person = self.polnoletna_oseba
		new_skrbnik = self.skrbnik_confirmed

		self.assertIsNotNone(new_person.rojen)
		self.assertIsNone(new_skrbnik.rojen)
		self.assertEqual(len(new_person.kontakti), 2)
		self.assertEqual(len(new_skrbnik.kontakti), 2)

		with self.case.db.transaction() as root:
			root.oseba.append(old_person)
			root.oseba.append(old_skrbnik)
			assert len(root.oseba) == 2

		status = await self.invoke(self.mladoletna_oseba, self.skrbnik, merged=True)
		self.assertEqualProperties(status, ['skrbnik', 'clan', 'validirani_podatki_clana', 'validirani_podatki_skrbnika'])

		with self.case.db.transaction() as root:
			self.assertEqual(len(root.oseba), 2)
			self.assertEqual(root.oseba[0].rojen, new_person.rojen)
			self.assertCountEqual(root.oseba[0].kontakti, kontakti_clana + self.polnoletna_oseba.kontakti)
			self.assertCountEqual(root.oseba[0].vpisi, self.polnoletna_oseba.vpisi + old_person.vpisi)
			self.assertEqual(root.oseba[0].tip_osebe, [TipOsebe.SKRBNIK, TipOsebe.CLAN])

			self.assertEqual(root.oseba[1].rojen, new_skrbnik.rojen)
			self.assertCountEqual(root.oseba[1].kontakti, kontakti_skrbnika + self.skrbnik.kontakti)
			self.assertCountEqual(root.oseba[1].vpisi, self.skrbnik.vpisi + old_skrbnik.vpisi)
			self.assertEqual(root.oseba[1].tip_osebe, [TipOsebe.SKRBNIK, TipOsebe.CLAN])

	async def test_mladoletnik_chuck_noris(self):
		self.mladoletna_oseba.kontakti[0].data = self.skrbnik.kontakti[0].data
		status = await self.invoke(self.mladoletna_oseba, self.skrbnik, db_saved=False)
		self.assertEqualProperties(status, ['skrbnik', 'clan', 'validirani_podatki_clana', 'validirani_podatki_skrbnika', 'razlogi_prekinitve'])
		self.assertCountEqual(status.razlogi_prekinitve, [TipProblema.CHUCK_NORIS])

	async def test_mladoletnik_napacni_podatki(self):
		self.mladoletna_oseba.kontakti[0].validacija = TipValidacije.VALIDIRAN
		self.validate_kontakts_existances.invoke.side_effect = lambda *kontakti: self.mladoletna_oseba.kontakti + self.skrbnik.kontakti

		status = await self.invoke(self.mladoletna_oseba, self.skrbnik, db_saved=False)
		self.assertEqualProperties(status, ['skrbnik', 'clan', 'validirani_podatki_clana', 'validirani_podatki_skrbnika', 'razlogi_prekinitve'])
		self.assertCountEqual(status.razlogi_prekinitve, [TipProblema.NAPAKE])

	async def test_mladoletnik_hacker(self):
		self.validate_kontakts_existances.invoke.side_effect = lambda *kontakti: self.mladoletna_oseba.kontakti + self.skrbnik.kontakti
		self.mladoletna_oseba.kontakti[0].data = self.skrbnik.kontakti[0].data

		status = await self.invoke(self.mladoletna_oseba, self.skrbnik, db_saved=False)
		self.assertEqualProperties(status, ['skrbnik', 'clan', 'validirani_podatki_clana', 'validirani_podatki_skrbnika', 'razlogi_prekinitve'])
		self.assertCountEqual(status.razlogi_prekinitve, [TipProblema.CHUCK_NORIS, TipProblema.NAPAKE, TipProblema.HACKER])


if __name__ == '__main__':
	unittest.main()
