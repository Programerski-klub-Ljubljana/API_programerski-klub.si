from dataclasses import dataclass
from datetime import datetime, date
from enum import auto

from unidecode import unidecode

from core import cutils
from core.domain._entity import elist, Elist, Entity
from core.domain._enums import EntityEnum


class TipKontakta(EntityEnum):
	EMAIL = auto()
	PHONE = auto()


class TipValidacije(EntityEnum):
	NI_VALIDIRAN = auto()
	VALIDIRAN = auto()
	POTRJEN = auto()


class TipOsebe(EntityEnum):
	CLAN = auto()
	SKRBNIK = auto()

	@classmethod
	def scopes(cls):
		return {k: f'Dovoljenje za {k}' for k in TipOsebe.values()}


@dataclass
class Kontakt:
	data: str
	tip: TipKontakta
	validacija: TipValidacije = TipValidacije.NI_VALIDIRAN


@dataclass
class Oseba(Entity):
	ime: str
	priimek: str
	rojen: date | None
	tip_osebe: elist[TipOsebe]
	geslo: str = None
	vpisi: elist[datetime] = Elist()
	izpisi: elist[datetime] = Elist()
	kontakti: elist[Kontakt] = Elist()

	def __post_init__(self):
		Entity.save(self)

	def __eq__(self, clan):
		return self.ime == clan.ime and self.priimek == clan.priimek and self.rojen == clan.rojen

	def has_username(self, username: str) -> bool:
		for kontakt in self.kontakti:
			if kontakt.data == username:
				return True

	def dodaj_kontakte(self, *kontakti: Kontakt):
		for kontakt in kontakti:
			obstaja = True
			for old_kontakt in self.kontakti:
				if old_kontakt.data == kontakt.data:
					obstaja = False
					break
			if not obstaja:
				self.kontakti.append(kontakt)

	def __str__(self):
		rojstvo_id = self.rojen.strftime("%d%m%Y")
		return unidecode(f'{self.ime}{self.priimek}_{rojstvo_id}'.replace(' ', '').lower())

	def nov_vpis(self):
		if not self.vpisan:
			self.vpisi.append(datetime.utcnow())

	@property
	def starost(self) -> float:
		return cutils.age(
			year=self.rojen.year,
			month=self.rojen.month,
			day=self.rojen.day)

	@property
	def mladoletnik(self) -> bool:
		return self.starost < 18

	@property
	def vpisan(self) -> bool:
		if len(self.izpisi) == 0:
			if len(self.vpisi) > 0:
				return True
			else:
				return False

		zadnji_vpis = self.vpisi[-1]
		zadnji_izpis = self.izpisi[-1]

		return zadnji_vpis > zadnji_izpis


@dataclass
class Ekipa(Entity):
	ime: str
	opis: str

	def __post_init__(self):
		Entity.save(self)


@dataclass
class Oddelek(Entity):
	ime: str
	opis: str
	ekipe: elist[Ekipa] = Elist()

	def __post_init__(self):
		Entity.save(self)


@dataclass
class Klub(Entity):
	ime: str
	clanarina: float
	oddelki: elist[Oddelek] = Elist()

	def __post_init__(self):
		Entity.save(self)
