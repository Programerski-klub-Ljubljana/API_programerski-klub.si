from dataclasses import dataclass
from datetime import datetime, date
from enum import auto

from core import cutils
from core.domain._entity import elist, Elist, Entity
from core.domain._enums import EntityEnum


class Dovoljenja(EntityEnum):
	READ = auto()
	WRITE = auto()
	EXEC = auto()

	@classmethod
	def scopes(cls):
		return {k: f'Dovoljenje za {k}' for k in Dovoljenja._member_names_}


class TipKontakta(EntityEnum):
	SKRBNIK = auto()
	OSTALO = auto()


@dataclass
class Kontakt(Entity):
	ime: str
	priimek: str
	tip: TipKontakta
	email: elist[str] = Elist()
	telefon: elist[str] = Elist()

	def __post_init__(self):
		Entity.save(self)


@dataclass
class Clan(Entity):
	ime: str
	priimek: str
	rojen: date
	geslo: str
	dovoljenja: elist[Dovoljenja] = Elist()

	email: elist[str] = Elist()
	telefon: elist[str] = Elist()
	skrbniki: elist[Kontakt] = Elist()

	# DATUMI
	vpisi: elist[datetime] = Elist()
	izpisi: elist[datetime] = Elist()

	def __post_init__(self):
		Entity.save(self)

	@property
	def starost(self) -> float:
		return cutils.age(
			year=self.rojen.year,
			month=self.rojen.month,
			day=self.rojen.day)

	@property
	def mladoletnik(self) -> bool:
		return self.starost < 18

	@property
	def vpisan(self) -> bool:
		if len(self.izpisi) == 0:
			if len(self.vpisi) > 0:
				return True
			else:
				return False

		zadnji_vpis = self.vpisi[-1]
		zadnji_izpis = self.izpisi[-1]

		return zadnji_vpis > zadnji_izpis


@dataclass
class Ekipa(Entity):
	ime: str
	opis: str

	def __post_init__(self):
		Entity.save(self)


@dataclass
class Oddelek(Entity):
	ime: str
	opis: str
	ekipe: elist[Ekipa] = Elist()

	def __post_init__(self):
		Entity.save(self)


@dataclass
class Klub(Entity):
	ime: str
	clanarina: float
	oddelki: elist[Oddelek] = Elist()

	def __post_init__(self):
		Entity.save(self)
