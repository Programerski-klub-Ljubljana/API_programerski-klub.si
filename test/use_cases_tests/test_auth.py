import unittest

from app import APP
from core.services.auth_service import Token

raise Exception('YOU STAYED HERE TESTING USER CASES!!!')

class test_auth(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=True)

		# USE CASE
		cls.auth_login = APP.useCases.auth_login()

	def test_login_pass(self):
		user = self.auth_login.invoke('urosjarc', 'geslo')
		self.assertIsInstance(user, Token)

	def test_login_fail(self):
		user = self.auth_login.invoke('urosjar', 'urosjarc')
		self.assertNotIsInstance(user, Token)


if __name__ == '__main__':
	unittest.main()
