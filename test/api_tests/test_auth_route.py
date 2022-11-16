import unittest

from starlette.testclient import TestClient

from api import main as api
from app import app


class test_auth_route(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		app.init(seed=True)
		api.init()
		cls.client = TestClient(api.api)

	def test_login_fail(self):
		res = self.client.post('/auth/login', data={'username': 'asdf', 'password': 'adsf'})
		body = res.json()
		self.assertEqual(body['detail'], 'Incorrect username or password')

	def test_login_success(self):
		res = self.client.post('/auth/login', data={'username': 'urosjarc', 'password': 'urosjarc'})
		body = res.json()
		self.assertListEqual(list(body.keys()), ['access_token', 'token_type'])


if __name__ == '__main__':
	unittest.main()
