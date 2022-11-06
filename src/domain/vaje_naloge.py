from enum import auto

from src.domain.__init__ import Entity, EntityEnum


class Naloga(Entity):
	class Tezavnost(EntityEnum):
		PREPROSTA = auto()
		LAHKA = auto()
		NORMALNA = auto()
		TEZKA = auto()
		NEMOGOCA = auto()

	ime: str
	opis: str
	stevilo_algoritmov: int
	tezavnost_algoritmov: Tezavnost
	tezavnost_struktur: Tezavnost
	koda: str
