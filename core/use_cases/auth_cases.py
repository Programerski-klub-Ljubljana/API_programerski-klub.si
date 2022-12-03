from dataclasses import dataclass
from datetime import timedelta

from autologging import traced

from app import CONST
from core.domain.arhitektura_kluba import Oseba
from core.services.auth_service import AuthService, Token, TokenData
from core.services.db_service import DbService
from core.use_cases._usecase import UseCase


@traced
@dataclass
class Auth_login(UseCase):
	db: DbService
	auth: AuthService

	def invoke(self, username, password) -> Token | None:
		for oseba in self.db.oseba_find(username):
			if self.auth.verify(password=password, hashed_password=oseba.geslo):
				return self.auth.encode(TokenData(username), expiration=timedelta(hours=CONST.auth_token_life))
		return None


@traced
@dataclass
class Auth_info(UseCase):
	db: DbService
	auth: AuthService

	def invoke(self, token: Token) -> Oseba | None:
		token_data = self.auth.decode(token.data)
		if token_data is None:
			return None
		for oseba in self.db.oseba_find(token_data.u):
			return oseba


@traced
@dataclass
class Auth_verification_token(UseCase):
	db: DbService
	auth: AuthService

	def invoke(self, username: str) -> Token:
		return self.auth.encode(TokenData(username=username), expiration=timedelta(hours=CONST.auth_verification_token_life))
