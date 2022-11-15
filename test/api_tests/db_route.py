import unittest

from starlette.testclient import TestClient

from api.main import api
from app import app


class test_db_route(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		app.init(seed=True)
		cls.client = TestClient(api)

	def test_openapi(self):
		res = self.client.get('/openapi.json')
		print(res.json())

	# def test_db_table_path(self):
	# 	res = self.client.get('/db/clan/0')
	# 	print(res.json())
	# 	self.assertEqual(res.status_code, 200)
	# 	self.assertIsInstance(res.json()['ime'], str)


if __name__ == '__main__':
	unittest.main()
