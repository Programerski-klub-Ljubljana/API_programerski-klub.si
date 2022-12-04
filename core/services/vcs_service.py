from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime

from autologging import traced


@dataclass
class VcsRepo:
	name: str
	html_url: str
	description: str
	fork: bool
	language: str
	forks_count: int
	stargazers_count: int
	watchers_count: int
	size: int
	default_branch: str
	open_issues_count: int
	topics: int
	visibility: str
	pushed_at: str
	created_at: str
	updated_at: str


@dataclass
class VcsOrganization:
	avatar_url: str
	description: str
	name: str
	company: str
	location: str
	email: str
	public_repos: int
	followers: int
	following: int
	html_url: str
	created_at: datetime
	updated_at: datetime
	total_private_repos: int
	owned_private_repos: int
	private_gists: int
	disk_usage: int
	collaborators: int
	repos: list[VcsRepo]


@traced
class VcsService(ABC):
	@abstractmethod
	def organization(self) -> VcsOrganization:
		pass
