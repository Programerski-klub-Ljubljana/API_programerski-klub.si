from datetime import datetime
from enum import auto

from src.domain.__init__ import EntityEnum, Entity


class DogodekTip(EntityEnum):
	TEKMA = auto()
	TRENING = auto()
	SRECANJE = auto()
	UPRAVNI_ODBOR = auto()


class Dogodek(Entity):
	ime: str
	opis: str
	trajanje: float
	tip: DogodekTip
	zacetek: datetime
	konec: datetime
