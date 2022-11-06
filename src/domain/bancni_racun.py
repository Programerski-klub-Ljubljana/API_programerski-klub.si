from dataclasses import dataclass
from datetime import date
from enum import auto

from persistent.list import PersistentList

from src.domain._entity import Entity, Elist, elist
from src.domain._enums import EntityEnum


class TipTransakcije(EntityEnum):
	PRIHODEK = auto()
	ODHODEK = auto()


class KategorijaTransakcije(EntityEnum):
	CLANARINA = auto()
	PLACA = auto()
	STROSKI = auto()
	OPREMA = auto()


@dataclass
class Transakcija(Entity):
	tip: TipTransakcije
	kategorija: KategorijaTransakcije
	rok: date
	opis: str
	znesek: float
	placano: float = 0


@dataclass
class BancniRacun(Entity):
	ime: str
	stevilka: str
	transakcije: elist[Transakcija] = Elist()

	def stanje(self) -> float:
		vsota = 0
		for t in self.transakcije:
			predznak = -1 if t.tip == TipTransakcije.ODHODEK else 1
			vsota += predznak * t.placano
		return vsota

	def dolgovi(self, transakcijskiTip: TipTransakcije) -> list[Transakcija]:
		dolgovi = []
		for t in self.transakcije:
			if t.tip == transakcijskiTip and t.placano < t.znesek:
				dolgovi.append(t)
		return dolgovi
