import unittest

from app import app
from core.services.db_service import DbService


class test_auth(unittest.TestCase):

	def setUp(self) -> None:
		app.init()
		self.service: DbService = app.adapters.db()

	def test_path(self):
		print(self.service.path('clan', '/'))

if __name__ == '__main__':
	unittest.main()
