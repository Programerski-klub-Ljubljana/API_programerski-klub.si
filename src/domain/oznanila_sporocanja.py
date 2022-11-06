from enum import auto

from src.domain.__init__ import EnumEntity, Entity


class ObjavaTip(EnumEntity):
	ZAPOSLOVANJE = auto()
	NOTRANJA = auto()
	ZUNANJA = auto()


class Objava(Entity):
	naslov: str
	template: str
	body: str


class SporociloTip(EnumEntity):
	EMAIL = auto()
	SMS = auto()
	KONTAKT = auto()


class Sporocilo(Entity):
	tip: SporociloTip
	template: str
	body: str
