from dataclasses import dataclass
from datetime import date

from core.domain._entity import Elist, elist, Entity
from core.domain._enums import EntityEnum


class TipTransakcije(EntityEnum):
	PRIHODEK = 'PRIHODEK'
	ODHODEK = 'ODHODEK'


class KategorijaTransakcije(EntityEnum):
	CLANARINA = "CLANARINA"
	PLACA = "PLACA"
	STROSKI = "STROSKI"
	OPREMA = "OPREMA"


@dataclass
class Transakcija(Entity):
	tip: TipTransakcije
	kategorija: KategorijaTransakcije
	rok: date
	opis: str
	znesek: float
	placano: float = 0


@dataclass
class Bancni_racun(Entity):
	ime: str
	stevilka: str
	transakcije: elist[Transakcija] = Elist.field()

	@property
	def stanje(self) -> float:
		vsota = 0
		for t in self.transakcije:
			predznak = -1 if t.tip == TipTransakcije.ODHODEK else 1
			vsota += predznak * t.placano
		return vsota

	def dolgovi(self, tip_transakcije: TipTransakcije) -> list[Transakcija]:
		dolgovi = []
		for t in self.transakcije:
			if t.tip == tip_transakcije and t.placano < t.znesek:
				dolgovi.append(t)
		return dolgovi
