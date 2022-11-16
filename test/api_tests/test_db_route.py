import unittest

from starlette.testclient import TestClient

from api import main as api
from app import app


class test_db_route(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		app.init(seed=True)
		api.init()
		cls.client = TestClient(api.api)

	def test_db_table_path(self):
		res = self.client.get('/db/clan/0')
		body = res.json()
		self.assertEqual(res.status_code, 200)
		self.assertIsInstance(body['ime'], str)
		self.assertEqual(body['_razred'], 'CLAN')


if __name__ == '__main__':
	unittest.main()
