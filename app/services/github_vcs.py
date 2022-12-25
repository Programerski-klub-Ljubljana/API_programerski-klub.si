import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

import requests
from autologging import traced
from github import GithubIntegration, Github, GithubException
from github.NamedUser import NamedUser
from github.Organization import Organization
from github.Repository import Repository

from core import cutils
from core.services.vcs_service import VcsService, VcsOrganization, VcsRepo, VcsMemberRole, VcsUser

log = logging.getLogger(__name__)


@dataclass
class GithubObj(ABC):

	@staticmethod
	@abstractmethod
	def parse(obj):
		pass


@dataclass
class GithubUser(VcsUser, GithubObj):
	instance: NamedUser = None

	@staticmethod
	def parse(obj: NamedUser):
		vcs_user = VcsUser()

		for k, v in vcs_user.__dict__.items():
			vcs_user.__dict__[k] = getattr(obj, k, None)

		vcs_user.instance = obj
		return vcs_user


@traced
class GithubVcs(VcsService):
	def __init__(self, app_id: str, private_key_path: str, organization: str):
		self.organization_name = organization
		self.github: Github | None = None
		self.org: Organization | None = None
		with open(cutils.root_path(private_key_path)) as f:
			self.github_integration = GithubIntegration(
				integration_id=app_id,
				private_key=f.read())
		self.init()

	def init(self):
		body = requests.get(f"https://api.github.com/orgs/{self.organization_name}/installation", headers={
			"Authorization": f"Bearer {self.github_integration.create_jwt(9 * 60)}"
		}).json()
		access = self.github_integration.get_access_token(installation_id=body.get('id', None))
		self.github = Github(login_or_token=access.token)
		self.org = self.github.get_organization(login=self.organization_name)

	def organization(self):
		repos: list[Repository] = self.org.get_repos().get_page(0)

		vcs_repos = []
		for r in repos:
			vcs_repos.append(cutils.call(VcsRepo, **r.raw_data))

		return cutils.call(VcsOrganization, **self.org.raw_data, repos=vcs_repos)

	def user(self, email: str) -> GithubUser | VcsUser | None:
		users = self.github.search_users(query=f"{email} in:email")
		if len(users.get_page(0)) > 0:
			return GithubUser.parse(users[0])

	def user_invite(self, email: str, member_role: VcsMemberRole) -> bool:
		try:
			self.org.invite_user(email=email, role=member_role.value)
		except GithubException as err:
			log.error(err)
			return False
		for user in self.org.invitations():
			if user.email == email:
				return True
		return False

	def user_remove(self, email: str) -> bool:
		user = self.user(email=email)

		if user is None:
			return True

		self.org.remove_from_membership(member=user.instance)
		return not self.org.has_in_members(user.instance)
