import unittest

from app import app


class test_validate(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		app.init(seed=True)

		# USE CASE
		cls.db_path = app.useCases.db_path()

	def test_db_path_0(self):
		result = self.db_path.invoke(table='clan', path=None, per_page=5)
		self.assertEqual(len(result), 5)
		self.assertIsInstance(result[0]['ime'], str)

	def test_db_path_1(self):
		try:
			self.db_path.invoke(table='clani', path=None, per_page=5)
		except Exception as err:
			self.assertEqual(str(err), "'ZoDbRoot' object has no attribute 'clani'")


if __name__ == '__main__':
	unittest.main()
