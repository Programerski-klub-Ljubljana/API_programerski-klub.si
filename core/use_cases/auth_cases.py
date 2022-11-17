from dataclasses import dataclass
from datetime import timedelta

from autologging import traced

from app import ENV
from core.services.auth_service import AuthService, Token
from core.services.db_service import DbService


@dataclass
class UserUseCase:
	authService: AuthService
	dbService: DbService


@traced
class Auth_login(UserUseCase):
	def invoke(self, username, password) -> Token | None:
		with self.dbService.transaction() as root:
			clan = root.get_clan(username)
			if clan is not None and self.authService.verify(password=password, hashed_password=clan.geslo):
				return self.authService.encode({'username': clan.username}, expiration=timedelta(hours=ENV.TOKEN_EXPIRE))

			return None
