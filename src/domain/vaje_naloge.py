from enum import auto

from src.domain.__init__ import Entity, EnumEntity


class Naloga(Entity):
	class Tezavnost(EnumEntity):
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
