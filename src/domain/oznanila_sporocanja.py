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


class TipSporocila(EntityEnum):
	EMAIL = auto()
	SMS = auto()
	KONTAKT = auto()


@dataclass
class Sporocilo(Entity):
	tip: TipSporocila
	vsebina: str
