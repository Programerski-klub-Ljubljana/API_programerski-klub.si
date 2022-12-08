import unittest
from datetime import timedelta, datetime
from types import NoneType

from app import APP
from core.domain.arhitektura_kluba import Oseba, Kontakt, TipKontakta, NivoValidiranosti
from core.services.auth_service import Token, TokenData
from core.use_cases.auth_cases import Vpisi_osebo, Vpisne_informacije, Ustvari_osebni_zeton, Vclani_osebo, Izpisi_osebo


class test_vpisi_osebo(unittest.TestCase):
	oseba2 = None
	oseba = None
	hash = None
	geslo = None
	case = None

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.case: Vpisi_osebo = APP.cases.vpisi_osebo()

		cls.geslo = 'geslo'
		cls.hash = cls.case.auth.hash(cls.geslo)

		cls.oseba = Oseba(ime="ime", priimek="priimek", geslo=cls.hash, rojen=None, kontakti=[
			Kontakt("test@example.si", tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)
		])
		cls.oseba2 = Oseba(ime="ime", priimek="priimek", geslo=cls.hash, rojen=None, kontakti=[
			Kontakt("test2@example.si", tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN)
		])

		with cls.case.db.transaction() as root:
			root.oseba.clear()
			root.save(cls.oseba, cls.oseba2)
			assert len(root.oseba) == 2

	@classmethod
	def tearDownClass(cls) -> None:
		with cls.case.db.transaction() as root:
			root.oseba.clear()
			assert len(root.oseba) == 0

	def test_oseba_ni_najdena(self):
		token = self.case.exe('', '')
		self.assertIsInstance(token, NoneType)

	def test_oseba_najdena_vendar_nima_potrjenega_kontakta(self):
		token = self.case.exe(self.oseba2.kontakti[0].data, self.geslo)
		self.assertIsInstance(token, NoneType)

	def test_uporabnik_najden_napacen_password(self):
		token = self.case.exe(self.oseba.kontakti[0].data, f'{self.geslo}123')
		self.assertIsInstance(token, NoneType)

	def test_oseba_uspesno_vpisana(self):
		token = self.case.exe(self.oseba.kontakti[0].data, self.geslo)
		self.assertIsInstance(token, Token)
		self.assertGreater(len(token.data), 30)
		token_data = self.case.auth.decode(token.data)
		self.assertEqual(token_data.d, self.oseba._id)
		self.assertIsInstance(token_data, TokenData)


class test_vpisne_informacije(unittest.TestCase):
	oseba = None
	hash = None
	geslo = None
	case = None

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.case: Vpisne_informacije = APP.cases.preberi_informacije_osebnega_zetona()

		cls.oseba = Oseba(ime="ime", priimek="priimek", geslo=cls.hash, rojen=None, kontakti=[
			Kontakt("test@example.si", tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)
		])

		cls.token = cls.case.auth.encode(TokenData(cls.oseba.kontakti[0].data), expiration=timedelta(days=1))
		cls.token_bad = cls.case.auth.encode(TokenData('a' + cls.oseba.kontakti[0].data), expiration=timedelta(days=1))
		cls.token_fake = Token(data='data', type='bearer')

		with cls.case.db.transaction() as root:
			root.oseba.clear()
			root.save(cls.oseba)
			assert len(root.oseba) == 1

	@classmethod
	def tearDownClass(cls) -> None:
		with cls.case.db.transaction() as root:
			root.oseba.clear()
			assert len(root.oseba) == 0

	def test_pravilen_zeton(self):
		self.assertTrue(self.oseba.equal(self.case.exe(self.token)))

	def test_napacen_zeton(self):
		self.assertIsInstance(self.case.exe(self.token_bad), NoneType)

	def test_fake_zeton(self):
		self.assertIsInstance(self.case.exe(self.token_fake), NoneType)


class test_ustvari_osebni_zeton(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.case: Ustvari_osebni_zeton = APP.cases.ustvari_osebni_zeton()

	def test(self):
		token = self.case.exe('1234asdf')
		self.assertIsInstance(token, Token)
		tokenData = self.case.auth.decode(token.data)
		self.assertEqual(tokenData.d, '1234asdf')


class test_vclani_osebo(unittest.TestCase):
	def setUp(self):
		APP.init(seed=False)
		self.case: Vclani_osebo = APP.cases.vclani_osebo()

		self.oseba = Oseba(ime='ime0', priimek='priimek0', rojen=None, kontakti=[
			Kontakt(data='data0', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)])

		self.ze_vpisana_oseba = Oseba(ime='ime', priimek='priimek', vpisi=[datetime.now()], rojen=None, kontakti=[
			Kontakt(data='data1', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)])

		with self.case.db.transaction() as root:
			root.oseba.clear()
			root.save(self.oseba, self.ze_vpisana_oseba)

	def tearDown(self):
		with self.case.db.transaction() as root:
			root.oseba.clear()
			root.save(self.oseba)

	def test_vclanitev(self):
		self.assertFalse(self.oseba.vpisan)
		before = datetime.now()
		self.assertTrue(self.case.exe(self.oseba._id))
		after = datetime.now()

		with self.case.db.transaction() as root:
			vpisi = root.oseba[0].vpisi
			self.assertTrue(self.oseba.vpisan)
			self.assertTrue(before < vpisi[0] < after)

	def test_ze_vpisan(self):
		self.assertEqual(len(self.ze_vpisana_oseba.vpisi), 1)
		self.assertTrue(self.ze_vpisana_oseba.vpisan)
		self.assertFalse(self.case.exe(self.ze_vpisana_oseba._id))

		with self.case.db.transaction() as _:
			self.assertEqual(len(self.ze_vpisana_oseba.vpisi), 1)
			self.assertTrue(self.ze_vpisana_oseba.vpisan)

	def test_ni_najden(self):
		self.assertFalse(self.case.exe('xxx'))


class test_izpisi_osebo(unittest.TestCase):
	def setUp(self):
		APP.init(seed=False)
		self.case: Izpisi_osebo = APP.cases.izpisi_osebo()

		self.oseba = Oseba(ime='ime0', priimek='priimek0', rojen=None, vpisi=[datetime.now()], kontakti=[
			Kontakt(data='data0', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)])

		self.ze_izpisana_oseba = Oseba(ime='ime', priimek='priimek', izpisi=[datetime.now()], rojen=None, kontakti=[
			Kontakt(data='data1', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN)])

		with self.case.db.transaction() as root:
			root.oseba.clear()
			root.save(self.oseba, self.ze_izpisana_oseba)

	def tearDown(self):
		with self.case.db.transaction() as root:
			root.oseba.clear()
			root.save(self.oseba)

	def test_izpis(self):
		self.assertTrue(self.oseba.vpisan)
		before = datetime.now()
		self.assertTrue(self.case.exe(self.oseba._id))
		after = datetime.now()

		with self.case.db.transaction() as root:
			izpisi = root.oseba[0].izpisi
			self.assertFalse(self.oseba.vpisan)
			self.assertTrue(before < izpisi[0] < after)

	def test_ze_izpisan(self):
		self.assertEqual(len(self.ze_izpisana_oseba.izpisi), 1)
		self.assertFalse(self.ze_izpisana_oseba.vpisan)
		self.assertFalse(self.case.exe(self.ze_izpisana_oseba._id))

		with self.case.db.transaction() as _:
			self.assertEqual(len(self.ze_izpisana_oseba.izpisi), 1)
			self.assertFalse(self.ze_izpisana_oseba.vpisan)

	def test_ni_najden(self):
		self.assertFalse(self.case.exe('xxx'))


if __name__ == '__main__':
	unittest.main()
