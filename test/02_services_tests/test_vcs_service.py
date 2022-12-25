import unittest

import shortuuid

from app import APP, CONST
from core.services.vcs_service import VcsService, VcsMemberRole


class test_vcs_service(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		APP.init(seed=False)
		cls.service: VcsService = APP.services.vcs()
		cls.testing_email = 'urosjarc@programerski-klub.si'
		cls.random_email = shortuuid.uuid()

	def test_organization(self):
		org = self.service.organization()
		self.assertGreater(len(org.name), 5)
		self.assertGreater(len(org.repos), 5)

	def test_user(self):
		user0 = self.service.user(email=CONST.email)
		user1 = self.service.user(email=CONST.alt_email)
		user2 = self.service.user(email=self.testing_email)

		self.assertEqual(user0.email, CONST.email)
		self.assertEqual(user1.email, CONST.alt_email)
		self.assertIsNone(user2)

	# * USERINVITE

	def test_00_user_invite_unknown(self):
		self.assertFalse(self.service.user_invite(email=self.random_email, member_role=VcsMemberRole.DIRECT_MEMBER))

	def test_00_user_invite(self):
		self.assertTrue(self.service.user_invite(email=self.testing_email, member_role=VcsMemberRole.DIRECT_MEMBER))

	def test_01_user_invite_again(self):
		self.assertTrue(self.service.user_invite(email=self.testing_email, member_role=VcsMemberRole.DIRECT_MEMBER))

	def test_02_user_invite_member(self):
		self.assertFalse(self.service.user_invite(email=CONST.alt_email, member_role=VcsMemberRole.DIRECT_MEMBER))

	# * USER CANCEL INVITE

	def test_02_user_remove(self):
		self.assertTrue(self.service.user_remove(email=self.testing_email))

	def test_02_user_remove_unknown(self):
		self.assertTrue(self.service.user_remove(email=self.random_email))


if __name__ == '__main__':
	unittest.main()
