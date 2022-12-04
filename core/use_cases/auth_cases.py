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
class Vpisi_osebo(UseCase):
	db: DbService
	auth: AuthService

	def exe(self, username, password) -> Token | None:
		for oseba in self.db.oseba_find(username):
			if self.auth.verify(password=password, hashed_password=oseba.geslo):
				"""
					THIS SENDS OSEBA ID SINCE EMAILS ARE NOT UNIQUE AND CAN BE SHARED!
				"""
				return self.auth.encode(TokenData(data=oseba._id), expiration=timedelta(hours=CONST.auth_token_life))
		return None


@traced
@dataclass
class Vclani_osebo(UseCase):
	db: DbService
	auth: AuthService

	def exe(self, oseba_id: str) -> bool:
		# TODO: Here you have to activated payment subscription on stripe!
		vpisan = False
		for oseba in self.db.oseba_find(data=oseba_id):
			if oseba._id == oseba_id:
				if not oseba.vpisan:
					oseba.nov_vpis()
					vpisan = True
		return vpisan


@traced
@dataclass
class Izpisi_osebo(UseCase):
	db: DbService
	auth: AuthService

	def exe(self, oseba_id: str) -> bool:
		# TODO: Here you have to DE - activated payment subscription on stripe!
		izpisan = False
		for oseba in self.db.oseba_find(data=oseba_id):
			if oseba._id == oseba_id:
				if oseba.vpisan:
					oseba.nov_izpis()
					izpisan = True
		return izpisan


@traced
@dataclass
class Vpisne_informacije(UseCase):
	db: DbService
	auth: AuthService

	def exe(self, token: Token) -> Oseba | None:
		token_data = self.auth.decode(token.data)
		if token_data is None:
			return None
		for oseba in self.db.oseba_find(token_data.d):
			return oseba


@traced
@dataclass
class Ustvari_osebni_zeton(UseCase):
	db: DbService
	auth: AuthService

	def exe(self, data: str) -> Token:
		return self.auth.encode(TokenData(data=data), expiration=timedelta(hours=CONST.auth_verification_token_life))
