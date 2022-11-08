from dataclasses import dataclass
from datetime import datetime, date
from enum import auto

from src import utils
from src.db.entity import plist, Plist, Entity
from src.db.enums import EntityEnum


class TipKontakta(EntityEnum):
	STARS = auto()
	STARI_STARS = auto()
	OSTALO = auto()


@dataclass
class Kontakt(Entity):
	ime: str
	priimek: str
	tip: TipKontakta
	email: plist[str] = Plist()
	telefon: plist[str] = Plist()

	def __post_init__(self):
		self.entity: Entity = Entity()


@dataclass
class Clan(Entity):
	ime: str
	priimek: str
	rojen: date
	email: plist[str] = Plist()
	telefon: plist[str] = Plist()
	skrbniki: plist[Kontakt] = Plist()

	# DATUMI
	vpisi: plist[datetime] = Plist()
	izpisi: plist[datetime] = Plist()

	def __post_init__(self):
		self.entity: Entity = Entity()

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

	def __post_init__(self):
		self.entity: Entity = Entity()


@dataclass
class Oddelek(Entity):
	ime: str
	opis: str
	ekipe: plist[Ekipa] = Plist()

	def __post_init__(self):
		self.entity: Entity = Entity()


@dataclass
class Klub(Entity):
	ime: str
	clanarina: float
	oddelki: plist[Oddelek] = Plist()

	def __post_init__(self):
		self.entity: Entity = Entity()
