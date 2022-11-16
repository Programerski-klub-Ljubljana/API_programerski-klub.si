from dataclasses import dataclass
from datetime import timedelta

from app import ENV
from core.services.auth_service import AuthService, Token
from core.services.db_service import DbService


@dataclass
class UserUseCase:
	authService: AuthService
	dbService: DbService


class Auth_login(UserUseCase):
	def invoke(self, username, password) -> Token | None:
		clan = self.dbService.get_clan(username)

		if clan is not None and self.authService.verify(password, clan.geslo):
			return self.authService.encode({'username': clan.username}, expiration=timedelta(hours=ENV.TOKEN_EXPIRE))

		return None
