import sys
import unittest

from starlette.testclient import TestClient

from api import API

this = sys.modules[__name__]


class test_auth_login(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		API.init()
		cls.client = TestClient(API.fapi)
		cls.token = None

	def login(self):
		res = self.client.post('/auth/login', data={'username': 'urosjarc', 'password': 'geslo'})
		body = res.json()
		self.assertListEqual(list(body.keys()), ['access_token', 'token_type'])
		return body['access_token']

	def test_00_login_fail(self):
		res = self.client.post('/auth/login', data={'username': 'xxx', 'password': 'xxx'})
		body = res.json()
		self.assertEqual(body['detail'], 'Incorrect username or password')

	def test_01_login_success(self):
		self.login()

	def test_02_info_success(self):
		token = self.login()
		self.assertGreater(len(token), 0)
		res = self.client.get('/auth/info', headers={'Authorization': f"Bearer {token}"})
		body = res.json()
		self.assertEqual(body['ime'], 'Uroš')
		self.assertEqual(body['priimek'], 'Jarc')


if __name__ == '__main__':
	unittest.main()
