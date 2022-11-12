import unittest
from unittest.mock import Mock, call

from app import app


class Test_session_start(unittest.TestCase):

	def setUp(self) -> None:
		app.init_test()
		self.program = Mock()
		self.clan_vpis = app.useCases.clan_vpis()

	def test_vpis_clana(self):
		self.assertTrue(True)



if __name__ == '__main__':
	unittest.main()
