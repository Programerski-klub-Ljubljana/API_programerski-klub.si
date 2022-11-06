from dataclasses import dataclass
from datetime import datetime, date
from enum import auto

from src import utils
from src.domain._entity import Entity, elist, Elist
from src.domain._enums import EntityEnum


class TipKontakta(EntityEnum):
	STARS = auto()
	STARI_STARS = auto()
	OSTALO = auto()


@dataclass
class Kontakt(Entity):
	ime: str
	priimek: str
	tip: TipKontakta
	email: elist[str] = Elist()
	telefon: elist[str] = Elist()


@dataclass
class Clan(Entity):
	ime: str
	priimek: str
	rojen: date
	email: elist[str] = Elist()
	telefon: elist[str] = Elist()
	skrbniki: elist[Kontakt] = Elist()

	# DATUMI
	vpisi: elist[datetime] = Elist()
	izpisi: elist[datetime] = Elist()

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
	ekipe: elist[Ekipa] = Elist()


@dataclass
class Klub(Entity):
	oddelki: elist[Oddelek] = Elist()
