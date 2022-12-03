import unittest
from datetime import timedelta, datetime
from types import NoneType

from app import APP
from core.domain.arhitektura_kluba import Oseba, Kontakt, TipKontakta, TipValidacije
from core.services.auth_service import Token, TokenData
from core.use_cases.auth_cases import Auth_login, Auth_info, Auth_verification_token, Auth_signin, Auth_signout


class test_login(unittest.TestCase):
	oseba2 = None
	oseba = None
	hash = None
	geslo = None
	case = None

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.case: Auth_login = APP.useCases.auth_login()

		cls.geslo = 'geslo'
		cls.hash = cls.case.auth.hash(cls.geslo)

		cls.oseba = Oseba(ime="ime", priimek="priimek", geslo=cls.hash, rojen=None, kontakti=[
			Kontakt("test@example.si", tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)
		])
		cls.oseba2 = Oseba(ime="ime", priimek="priimek", geslo=cls.hash, rojen=None, kontakti=[
			Kontakt("test2@example.si", tip=TipKontakta.EMAIL, validacija=TipValidacije.VALIDIRAN)
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

	def test_user_not_found(self):
		token = self.case.invoke('', '')
		self.assertIsInstance(token, NoneType)

	def test_user_found_but_not_confirmed_kontakt(self):
		token = self.case.invoke(self.oseba2.kontakti[0].data, self.geslo)
		self.assertIsInstance(token, NoneType)

	def test_user_found_but_wrong_password(self):
		token = self.case.invoke(self.oseba.kontakti[0].data, f'{self.geslo}123')
		self.assertIsInstance(token, NoneType)

	def test_user_pass(self):
		token = self.case.invoke(self.oseba.kontakti[0].data, self.geslo)
		self.assertIsInstance(token, Token)
		self.assertGreater(len(token.data), 30)
		token_data = self.case.auth.decode(token.data)
		self.assertEqual(token_data.d, self.oseba._id)
		self.assertIsInstance(token_data, TokenData)


class test_info(unittest.TestCase):
	oseba = None
	hash = None
	geslo = None
	case = None

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.case: Auth_info = APP.useCases.auth_info()

		cls.oseba = Oseba(ime="ime", priimek="priimek", geslo=cls.hash, rojen=None, kontakti=[
			Kontakt("test@example.si", tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)
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

	def test_token_good(self):
		self.assertTrue(self.oseba.equal(self.case.invoke(self.token)))

	def test_token_bad(self):
		self.assertIsInstance(self.case.invoke(self.token_bad), NoneType)

	def test_token_fake(self):
		self.assertIsInstance(self.case.invoke(self.token_fake), NoneType)


class test_verification_token(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.case: Auth_verification_token = APP.useCases.auth_verification_token()

	def test_token_creation(self):
		token = self.case.invoke('1234asdf')
		self.assertIsInstance(token, Token)
		tokenData = self.case.auth.decode(token.data)
		self.assertEqual(tokenData.d, '1234asdf')


class test_signin(unittest.TestCase):
	def setUp(self):
		APP.init(seed=False)
		self.case: Auth_signin = APP.useCases.auth_signin()

		self.oseba = Oseba(ime='ime0', priimek='priimek0', rojen=None, kontakti=[
			Kontakt(data='data0', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)])

		self.ze_vpisana_oseba = Oseba(ime='ime', priimek='priimek', vpisi=[datetime.utcnow()], rojen=None, kontakti=[
			Kontakt(data='data1', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)])

		with self.case.db.transaction() as root:
			root.oseba.clear()
			root.save(self.oseba, self.ze_vpisana_oseba)

	def tearDown(self):
		with self.case.db.transaction() as root:
			root.oseba.clear()
			root.save(self.oseba)

	def test_pass(self):
		self.assertFalse(self.oseba.vpisan)
		before = datetime.utcnow()
		self.assertTrue(self.case.invoke(self.oseba._id))
		after = datetime.utcnow()

		with self.case.db.transaction() as root:
			vpisi = root.oseba[0].vpisi
			self.assertTrue(self.oseba.vpisan)
			self.assertTrue(before < vpisi[0] < after)

	def test_ze_vpisan(self):
		self.assertEqual(len(self.ze_vpisana_oseba.vpisi), 1)
		self.assertTrue(self.ze_vpisana_oseba.vpisan)
		self.assertFalse(self.case.invoke(self.ze_vpisana_oseba._id))

		with self.case.db.transaction() as _:
			self.assertEqual(len(self.ze_vpisana_oseba.vpisi), 1)
			self.assertTrue(self.ze_vpisana_oseba.vpisan)

	def test_ni_najden(self):
		self.assertFalse(self.case.invoke('xxx'))


class test_signout(unittest.TestCase):
	def setUp(self):
		APP.init(seed=False)
		self.case: Auth_signout = APP.useCases.auth_signout()

		self.oseba = Oseba(ime='ime0', priimek='priimek0', rojen=None, vpisi=[datetime.utcnow()], kontakti=[
			Kontakt(data='data0', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)])

		self.ze_izpisana_oseba = Oseba(ime='ime', priimek='priimek', izpisi=[datetime.utcnow()], rojen=None, kontakti=[
			Kontakt(data='data1', tip=TipKontakta.EMAIL, validacija=TipValidacije.POTRJEN)])

		with self.case.db.transaction() as root:
			root.oseba.clear()
			root.save(self.oseba, self.ze_izpisana_oseba)

	def tearDown(self):
		with self.case.db.transaction() as root:
			root.oseba.clear()
			root.save(self.oseba)

	def test_pass(self):
		self.assertTrue(self.oseba.vpisan)
		before = datetime.utcnow()
		self.assertTrue(self.case.invoke(self.oseba._id))
		after = datetime.utcnow()

		with self.case.db.transaction() as root:
			izpisi = root.oseba[0].izpisi
			self.assertFalse(self.oseba.vpisan)
			self.assertTrue(before < izpisi[0] < after)

	def test_ze_izpisan(self):
		self.assertEqual(len(self.ze_izpisana_oseba.izpisi), 1)
		self.assertFalse(self.ze_izpisana_oseba.vpisan)
		self.assertFalse(self.case.invoke(self.ze_izpisana_oseba._id))

		with self.case.db.transaction() as _:
			self.assertEqual(len(self.ze_izpisana_oseba.izpisi), 1)
			self.assertFalse(self.ze_izpisana_oseba.vpisan)

	def test_ni_najden(self):
		self.assertFalse(self.case.invoke('xxx'))




if __name__ == '__main__':
	unittest.main()
