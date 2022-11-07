from dataclasses import dataclass
from datetime import datetime
from enum import auto

from src.db.entity import plist, Plist, Entity
from src.db.enums import EntityEnum
from src.domain.arhitektura_kluba import Clan


class TipDogodka(EntityEnum):
	TEKMA = auto()
	TRENING = auto()
	SRECANJE = auto()
	UPRAVNI_ODBOR = auto()


@dataclass
class Dogodek(Entity):
	ime: str
	opis: str
	trajanje: float
	tip: TipDogodka
	zacetek: datetime
	konec: datetime
	clani: plist[Clan] = Plist()

	def __post_init__(self):
		self.entity: Entity = Entity()
