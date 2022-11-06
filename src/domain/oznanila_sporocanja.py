from enum import auto

from src.domain.__init__ import EntityEnum, Entity


class ObjavaTip(EntityEnum):
	ZAPOSLOVANJE = auto()
	NOTRANJA = auto()
	ZUNANJA = auto()


class Objava(Entity):
	naslov: str
	template: str
	body: str


class SporociloTip(EntityEnum):
	EMAIL = auto()
	SMS = auto()
	KONTAKT = auto()


class Sporocilo(Entity):
	tip: SporociloTip
	template: str
	body: str
