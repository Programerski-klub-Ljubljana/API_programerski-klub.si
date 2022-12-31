from dataclasses import dataclass
from enum import auto

from core.domain._entity import elist, Elist, Entity
from core.domain._enums import EntityEnum


class Tezavnost(EntityEnum):
	PREPROSTA = 'PREPROSTA'
	LAHKA = 'LAHKA'
	NORMALNA = 'NORMALNA'
	TEZKA = 'TEZKA'
	NEMOGOCA = 'NEMOGOCA'


@dataclass
class Naloga(Entity):
	ime: str
	opis: str
	stevilo_algoritmov: int
	tezavnost_algoritmov: Tezavnost
	tezavnost_struktur: Tezavnost
	koda: str
	test: str


@dataclass
class Test(Entity):
	ime: str
	opis: str
	naloge: elist[Naloga] = Elist.field()
