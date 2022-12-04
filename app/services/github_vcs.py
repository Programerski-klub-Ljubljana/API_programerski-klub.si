import logging

import requests
from autologging import traced
from github import GithubIntegration, Github
from github.Repository import Repository

from core import cutils
from core.services.vcs_service import VcsService, VcsOrganization, VcsRepo

log = logging.getLogger(__name__)


@traced
class GithubVcs(VcsService):
	def __init__(self, app_id: str, private_key_path: str, organization: str):
		self.organization_name = organization
		self.github: Github | None = None
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

	def organization(self):
		org = self.github.get_organization(login=self.organization_name)
		repos: list[Repository] = org.get_repos().get_page(0)

		vcs_repos = []
		for r in repos:
			vcs_repos.append(cutils.call(VcsRepo, **r.raw_data))

		return cutils.call(VcsOrganization, **org.raw_data, repos=vcs_repos)
