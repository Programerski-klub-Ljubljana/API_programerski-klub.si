from dataclasses import dataclass
from datetime import timedelta

from autologging import traced

from app import ENV
from core import cutils
from core.services.auth_service import AuthService, Token, TokenData
from core.services.db_service import DbService


@dataclass
class AuthUserCase:
	authService: AuthService
	dbService: DbService


@traced
class Auth_login(AuthUserCase):
	def invoke(self, username, password) -> Token | None:
		with self.dbService.transaction() as root:
			clan = root.get_clan(username)
			if clan is not None and self.authService.verify(password=password, hashed_password=clan.geslo):
				return self.authService.encode(TokenData(clan.username), expiration=timedelta(hours=ENV.TOKEN_EXPIRE))

			return None


@traced
class Auth_info(AuthUserCase):
	def invoke(self, token) -> dict:
		token_data = self.authService.decode(token)
		with self.dbService.transaction() as root:
			return cutils.object_json(root.get_clan(token_data.username))
