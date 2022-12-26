import unittest

import shortuuid

from app import APP, CONST
from core.services.vcs_service import VcsService, VcsMemberRole


class test_vcs_service(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		APP.init(seed=False)
		cls.service: VcsService = APP.services.vcs()
		cls.non_existing_email = shortuuid.uuid()
		cls.is_vcs_member = CONST.emails.test_vcs_member
		cls.doesnt_have_vcs_profile = CONST.emails.test2

	def test_organization(self):
		org = self.service.organization()
		self.assertGreater(len(org.name), 5)
		self.assertGreater(len(org.repos), 5)

	def test_user(self):
		member = self.service.user(email=self.is_vcs_member)
		doesnt_have_vcs_profile = self.service.user(email=self.doesnt_have_vcs_profile)

		self.assertEqual(member.email, self.is_vcs_member)
		self.assertIsNone(doesnt_have_vcs_profile)

	# * USERINVITE

	def test_00_user_invite_unknown(self):
		self.assertFalse(self.service.user_invite(email=self.non_existing_email, member_role=VcsMemberRole.DIRECT_MEMBER))

	def test_00_user_invite(self):
		self.assertTrue(self.service.user_invite(email=self.doesnt_have_vcs_profile, member_role=VcsMemberRole.DIRECT_MEMBER))

	def test_01_user_invite_again(self):
		self.assertTrue(self.service.user_invite(email=self.doesnt_have_vcs_profile, member_role=VcsMemberRole.DIRECT_MEMBER))

	def test_02_user_invite_member(self):
		self.assertFalse(self.service.user_invite(email=self.is_vcs_member, member_role=VcsMemberRole.DIRECT_MEMBER))

	# * USER CANCEL INVITE

	def test_02_user_remove(self):
		self.assertTrue(self.service.user_remove(email=self.doesnt_have_vcs_profile))

	def test_02_user_remove_unknown(self):
		self.assertTrue(self.service.user_remove(email=self.non_existing_email))


if __name__ == '__main__':
	unittest.main()
