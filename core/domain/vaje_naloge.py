from dataclasses import dataclass
from enum import auto

from core.domain._entity import elist, Elist, Entity
from core.domain._enums import EntityEnum


class Tezavnost(EntityEnum):
	PREPROSTA = auto()
	LAHKA = auto()
	NORMALNA = auto()
	TEZKA = auto()
	NEMOGOCA = auto()


@dataclass
class Naloga(Entity):
	ime: str
	opis: str
	stevilo_algoritmov: int
	tezavnost_algoritmov: Tezavnost
	tezavnost_struktur: Tezavnost
	koda: str
	test: str

	def __post_init__(self):
		self.entity: Entity = Entity(self)


@dataclass
class Test(Entity):
	ime: str
	opis: str
	naloge: elist[Naloga] = Elist.field()

	def __post_init__(self):
		self.entity: Entity = Entity(self)
