import unittest

from app import APP


class test_validate(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)

		# USE CASE
		cls.db_path = APP.useCases.db_path()

	def test_db_path_0(self):
		result = self.db_path.invoke(table='oseba', path=None, per_page=5)
		self.assertEqual(len(result), 5)
		self.assertIsInstance(result[0]['ime'], str)

	def test_db_path_1(self):
		try:
			self.db_path.invoke(table='osebi', path=None, per_page=5)
		except Exception as err:
			self.assertEqual(str(err), "'ZoDbRoot' object has no attribute 'osebi'")


if __name__ == '__main__':
	unittest.main()
