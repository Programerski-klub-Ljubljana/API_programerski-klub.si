import unittest

from app import APP
from core.services.vcs_service import VcsService


class test_github(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		APP.init(seed=False)

		cls.service: VcsService = APP.services.vcs()

	def test_organization(self):
		org = self.service.organization()
		self.assertGreater(len(org.name), 5)
		self.assertGreater(len(org.repos), 5)


if __name__ == '__main__':
	unittest.main()
