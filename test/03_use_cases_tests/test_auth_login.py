import unittest

from app import APP, CONST
from core.domain.arhitektura_kluba import Oseba
from core.services.auth_service import Token
from core.use_cases.auth_cases import Auth_info


class test_auth_login(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)

		# USE CASE
		cls.auth_login = APP.useCases.auth_login()
		cls.auth_info: Auth_info = APP.useCases.auth_info()

	def login(self):
		return self.auth_login.invoke(CONST.alt_email, 'geslo')

	def test_00_login_pass(self):
		token = self.login()
		self.assertIsInstance(token, Token)

	def test_01_login_fail(self):
		token = self.auth_login.invoke('janeznova', 'janeznovak')
		self.assertNotIsInstance(token, Token)

	def test_02_info_pass(self):
		token = self.login()
		info = self.auth_info.invoke(token.data)
		self.assertIsInstance(info, Oseba)


if __name__ == '__main__':
	unittest.main()
