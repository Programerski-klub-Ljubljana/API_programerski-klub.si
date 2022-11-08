from dataclasses import dataclass
from enum import auto

from src.db.entity import Entity
from src.db.enums import EntityEnum


class TipObjave(EntityEnum):
	ZAPOSLOVANJE = auto()
	NOTRANJA = auto()
	ZUNANJA = auto()


@dataclass
class Objava(Entity):
	tip: TipObjave
	naslov: str
	opis: str
	vsebina: str

	def __post_init__(self):
		self.entity: Entity = Entity(self)


class TipSporocila(EntityEnum):
	EMAIL = auto()
	SMS = auto()
	FORMS_KONTAKT = auto()
	FORMS_VPIS = auto()


@dataclass
class Sporocilo(Entity):
	tip: TipSporocila
	vsebina: str

	def __post_init__(self):
		self.entity: Entity = Entity(self)
