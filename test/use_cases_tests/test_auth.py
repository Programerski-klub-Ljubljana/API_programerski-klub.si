import time
import unittest

from app import APP
from core.services.auth_service import Token, AuthService


class test_auth(unittest.TestCase):

	def setUp(self) -> None:
		APP.init(seed=True)

		# USE CASE
		self.auth_service: AuthService = APP.services.auth()
		self.auth_login = APP.useCases.auth_login()


	def test_login_pass(self):
		token = self.auth_login.invoke('urosjarc', 'geslo')
		self.assertIsInstance(token, Token)

	def test_login_fail(self):
		token = self.auth_login.invoke('urosjar', 'urosjarc')
		self.assertNotIsInstance(token, Token)


if __name__ == '__main__':
	unittest.main()
