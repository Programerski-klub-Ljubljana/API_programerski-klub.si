from dataclasses import dataclass
from datetime import datetime
from enum import auto

from core.domain._entity import elist, Elist, Entity
from core.domain._enums import EntityEnum
from core.domain.arhitektura_kluba import Oseba


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
	clani: elist[Oseba] = Elist.field()

	def __post_init__(self):
		self.entity: Entity = Entity(self)
