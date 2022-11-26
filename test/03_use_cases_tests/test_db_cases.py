import unittest

from app import APP
from core.domain.arhitektura_kluba import Oseba, Kontakt, TipKontakta
from core.use_cases.db_cases import Db_path


class test_path(unittest.TestCase):
	geslo = None
	case = None

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.case: Db_path = APP.useCases.db_path()

		with cls.case.db.transaction() as root:
			ks = [Kontakt(data='asdf1234', tip=TipKontakta.EMAIL) for j in range(10)]
			root.save(*[Oseba(ime="ime", priimek="priimek", rojen=None, kontakti=ks) for i in range(10)])
			assert len(root.oseba) == 10

	@classmethod
	def tearDownClass(cls) -> None:
		with cls.case.db.transaction() as root:
			root.oseba.clear()
			assert len(root.oseba) == 0

	def test_return(self):
		r = self.case.invoke(table='oseba', per_page=10, max_depth=100)
		for i in range(10):
			self.assertEqual(len(r), 10)
			self.assertIsInstance(r, list)
			self.assertIsInstance(r[i], dict)
			self.assertGreater(len(r[i].keys()), 5)
			self.assertIsInstance(r[i]['ime'], str)
			for j in range(10):
				self.assertEqual(r[i]['kontakti'][j]['data'], 'asdf1234')

	def test_pagination(self):
		r_all = self.case.invoke(table='oseba', per_page=10)

		r = self.case.invoke(table='oseba', per_page=5)
		self.assertEqual(r, r_all[:5])

		r = self.case.invoke(table='oseba', per_page=5, page=1)
		self.assertEqual(r, r_all[5:10])

		r = self.case.invoke(table='oseba', per_page=2, page=4)
		self.assertEqual(r, r_all[8:10])

	def test_max_depth(self):
		# 4
		r = self.case.invoke(table='oseba', per_page=10, max_depth=4)
		for ri in r:
			self.assertEqual(ri['kontakti'][0]['data'], 'asdf1234')

		# 3
		r = self.case.invoke(table='oseba', per_page=10, max_depth=3)
		for ri in r:
			self.assertEqual(ri['kontakti'][0], 'MAX_DEPTH_OBJECT')

		# 2
		r = self.case.invoke(table='oseba', per_page=10, max_depth=2)
		for ri in r:
			self.assertEqual(ri['kontakti'], 'MAX_DEPTH_LIST')

		# 1
		r = self.case.invoke(table='oseba', per_page=10, max_depth=1)
		for ri in r:
			self.assertEqual(ri, 'MAX_DEPTH_OBJECT')

	def test_max_width(self):
		r = self.case.invoke(table='oseba', per_page=10, max_depth=10, max_width=2)
		self.assertEqual(len(r), 3)
		self.assertIsInstance(r[0], dict)
		self.assertIsInstance(r[1], dict)
		self.assertEqual(r[2], 'MAX_WIDTH')

		for i in range(len(r)-1):
			ri = r[i]
			self.assertIsInstance(ri['kontakti'][0], dict, ri)
			self.assertIsInstance(ri['kontakti'][1], dict, ri)
			self.assertEqual(ri['kontakti'][2], 'MAX_WIDTH', ri)

	def test_fail(self):
		try:
			self.case.invoke(table='osebi')
		except Exception as err:
			self.assertEqual(str(err), "'ZoDbRoot' object has no attribute 'osebi'")


if __name__ == '__main__':
	unittest.main()
