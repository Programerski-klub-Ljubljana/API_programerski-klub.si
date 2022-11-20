from dataclasses import dataclass
from datetime import timedelta

from autologging import traced

from app import CONST
from core import cutils
from core.services.auth_service import AuthService, Token, TokenData
from core.services.db_service import DbService
from core.use_cases._usecase import UseCase


@traced
@dataclass
class Auth_login(UseCase):
	db: DbService
	auth: AuthService

	def invoke(self, username, password) -> Token | None:
		with self.db.transaction() as root:
			for clan in root.clan_find_all(username):
				if self.auth.verify(password=password, hashed_password=clan.geslo):
					return self.auth.encode(TokenData(clan.username), expiration=timedelta(hours=CONST.token_life))

			return None


@traced
@dataclass
class Auth_info(UseCase):
	db: DbService
	auth: AuthService

	def invoke(self, token) -> dict | None:
		token_data = self.auth.decode(token)
		if token_data is None:
			return None
		with self.db.transaction() as root:
			clan = root.clan_find_all(token_data.username)
			if clan is not None:
				return cutils.object_json(clan)
