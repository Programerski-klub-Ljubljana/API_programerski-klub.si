from dataclasses import dataclass
from datetime import datetime, date

from persistent.list import PersistentList

from src import utils
from src.domain import Entity


@dataclass
class Clan(Entity):
	ime: str
	priimek: str
	rojen: date
	email: list[str] = PersistentList()
	telefon: list[str] = PersistentList()

	# DATUMI
	vpisi: list[datetime] = PersistentList()
	izpisi: list[datetime] = PersistentList()

	@property
	def starost(self) -> float:
		return utils.age(
			year=self.rojen.year,
			month=self.rojen.month,
			day=self.rojen.day)

	@property
	def vpisan(self) -> bool:
		zadnji_vpis = self.vpisi[-1]

		if len(self.izpisi) == 0:
			return True

		zadnji_izpis = self.izpis[-1]
		return zadnji_vpis > zadnji_izpis


@dataclass
class Ekipa(Entity):
	ime: str
	opis: str


@dataclass
class Oddelek(Entity):
	ime: str
	opis: str
	ekipe: list[Ekipa] = PersistentList


@dataclass
class Klub(Entity):
	oddelki: list[Oddelek] | PersistentList = PersistentList()
