from dataclasses import dataclass
from enum import auto

from core.domain._entity import Entity
from core.domain._enums import EntityEnum


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


@dataclass
class Sporocilo(Entity):
	naslov: str
	vsebina: str
