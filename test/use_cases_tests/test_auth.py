import unittest

from app import app
from core.services.auth_service import Token


class test_auth(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		app.init(seed=True)

		# USE CASE
		cls.auth_login = app.useCases.auth_login()

	def test_login_pass(self):
		user = self.auth_login.invoke('urosjarc', 'urosjarc')
		self.assertIsInstance(user, Token)

	def test_login_fail(self):
		user = self.auth_login.invoke('urosjar', 'urosjarc')
		self.assertNotIsInstance(user, Token)


if __name__ == '__main__':
	unittest.main()
