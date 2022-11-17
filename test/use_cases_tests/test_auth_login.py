import unittest

from app import APP
from core.services.auth_service import Token
from core.use_cases.auth_cases import Auth_info


class test_auth_login(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=True)

		# USE CASE
		cls.auth_login = APP.useCases.auth_login()
		cls.auth_info: Auth_info = APP.useCases.auth_info()

	def login(self):
		return self.auth_login.invoke('urosjarc', 'geslo')

	def test_00_login_pass(self):
		token = self.login()
		self.assertIsInstance(token, Token)

	def test_01_login_fail(self):
		token = self.auth_login.invoke('urosjar', 'urosjarc')
		self.assertNotIsInstance(token, Token)

	def test_02_info_pass(self):
		token = self.login()
		info = self.auth_info.invoke(token.data)
		self.assertTrue('ime' in info)
		self.assertTrue('priimek' in info)


if __name__ == '__main__':
	unittest.main()
