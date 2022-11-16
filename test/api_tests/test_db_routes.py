import unittest

from starlette.testclient import TestClient

from api import API


class test_db(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		API.init()
		cls.client = TestClient(API.fapi)

	def test_db_table_path(self):
		res = self.client.get('/db/clan/0')
		body = res.json()
		self.assertEqual(res.status_code, 200)
		self.assertIsInstance(body['ime'], str)
		self.assertEqual(body['_razred'], 'CLAN')


if __name__ == '__main__':
	unittest.main()
