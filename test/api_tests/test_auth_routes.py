import sys
import unittest

from starlette.testclient import TestClient

from api import API

this = sys.modules[__name__]


class test_auth(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		API.init()
		cls.client = TestClient(API.fapi)
		cls.token = None

	def test_login_fail(self):
		res = self.client.post('/auth/login', data={'username': 'xxx', 'password': 'xxx'})
		body = res.json()
		self.assertEqual(body['detail'], 'Incorrect username or password')

	def test_login_success(self):
		res = self.client.post('/auth/login', data={'username': 'urosjarc', 'password': 'geslo'})
		body = res.json()
		self.assertListEqual(list(body.keys()), ['access_token', 'token_type'])
		self.token = body['access_token']


if __name__ == '__main__':
	unittest.main()
