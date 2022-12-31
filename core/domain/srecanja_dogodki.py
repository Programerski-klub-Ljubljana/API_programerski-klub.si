from dataclasses import dataclass
from datetime import datetime

from core.domain._entity import elist, Elist, Entity
from core.domain._enums import EntityEnum
from core.domain.arhitektura_kluba import Oseba


class TipDogodka(EntityEnum):
	TEKMA = "TEKMA"
	TRENING = "TRENING"
	SRECANJE = "SRECANJE"
	UPRAVNI_ODBOR = "UPRAVNI_ODBOR"


@dataclass
class Dogodek(Entity):
	ime: str
	opis: str
	trajanje: float
	tip: TipDogodka
	zacetek: datetime
	konec: datetime
	clani: elist[Oseba] = Elist.field()
