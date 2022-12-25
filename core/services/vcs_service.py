from abc import abstractmethod, ABC
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from autologging import traced


@dataclass
class VcsMemberRole(str, Enum):
	ADMIN = 'admin'
	DIRECT_MEMBER = 'direct_member'
	BILLING_MANAGER = 'billing_manager'


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


@dataclass
class VcsUser:
	instance: object = None
	avatar_url: str = None
	bio: str = None
	blog: str = None
	created_at: datetime = None
	email: str = None
	followers: int = None
	following: int = None
	html_url: str = None
	id: int = None
	location: str = None
	login: str = None
	name: str = None
	type: str = None
	updated_at: datetime = None
	url: str = None


@traced
class VcsService(ABC):
	@abstractmethod
	def organization(self) -> VcsOrganization:
		pass

	@abstractmethod
	def user(self, email: str) -> VcsUser | None:
		pass

	@abstractmethod
	def user_invite(self, email: str, member_role: VcsMemberRole) -> bool:
		pass

	@abstractmethod
	def user_remove(self, email: str):
		pass
