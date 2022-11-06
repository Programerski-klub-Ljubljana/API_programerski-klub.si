from dataclasses import dataclass
from datetime import datetime

from src.domain.utils import Entity, EnumEntity


class TransakcijaTip(EnumEntity):
	CLANARINA = 'CLANARINA'
	PLACA = 'PLACA'
	STROSKI = 'STROSKI'
	OPREMA = 'OPREMA'


@dataclass
class Transakcija(Entity):
	tip: TransakcijaTip
	znesek: float
	placano: float
	rok: datetime


class BancniRacun(Entity):
	trr: str
