from dataclasses import dataclass, field
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
class Kontakt(Entity):
	data: str
	tip: TipKontakta
	validacija: TipValidacije = TipValidacije.NI_VALIDIRAN

	def __eq__(self, kontakt):
		return self.data == kontakt.data


@dataclass
class Oseba(Entity):
	ime: str
	priimek: str
	rojen: date | None
	tip_osebe: elist[TipOsebe] = Elist.field()
	geslo: str = None
	vpisi: elist[datetime] = Elist.field()
	izpisi: elist[datetime] = Elist.field()
	kontakti: elist[Kontakt] = Elist.field()

	def __post_init__(self):
		Entity.save(self)

	def __eq__(self, oseba):
		# EQUACIJA MORA BITI MEHKA DA SE PREJ DETEKTIRAJO MOZNI DUPLIKATI
		if not (self.ime == oseba.ime and self.priimek == oseba.priimek):
			return False

		# CE SE PRIIMEK IN IME UJEMA IN DA DATUMA NISTA PRAZNA POTEM DATUM ROJSTVA ODLOCA ALI STA ISTA
		if self.rojen is not None and oseba.rojen is not None:
			return self.rojen == oseba.rojen

		# CE NIMA ROJSTVO DATUMA POGLEJ PO KONTAKTIH (NOBEN PODATKEN V BAZI NE BO OBSTAJAL DA NE BO VALIDIRAN)
		# PREJ BOM ZAVRNIL MUDELA PRI VPISU
		# OBVEZNO MORA IMETI KONTAKT POTRJEN DRUGACE LAHKO PRIDE DO ZLORAB
		for k1 in self.kontakti:
			for k2 in oseba.kontakti:
				if (
						k1 == k2 and
						k1.validacija == TipValidacije.POTRJEN and
						k2.validacija == TipValidacije.POTRJEN and
						k1.tip == k2.tip):
					return True

		return False

	def has_username(self, username: str) -> bool:
		for kontakt in self.kontakti:
			if kontakt.data == username and kontakt.validacija == TipValidacije.POTRJEN:
				return True
		return False

	def dodaj_kontakte(self, *kontakti: Kontakt):
		for kontakt in kontakti:
			if kontakt not in self.kontakti:
				self.kontakti.append(kontakt)

	def dodaj_tip_osebe(self, *statusi: TipOsebe):
		for status in statusi:
			if status not in self.tip_osebe:
				self.tip_osebe.append(status)

	def __str__(self):
		id = ''
		if self.rojen is not None:
			id = self.rojen.strftime("%d%m%Y")
		else:
			for k in self.kontakti:
				if k.validacija == TipValidacije.POTRJEN:
					id = k.data.replace('+', '')
		return unidecode(f'{self.ime}{self.priimek}_{id}'.replace(' ', '').lower())

	def nov_vpis(self):
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
	ekipe: elist[Ekipa] = Elist.field()

	def __post_init__(self):
		Entity.save(self)


@dataclass
class Klub(Entity):
	ime: str
	clanarina: float
	oddelki: elist[Oddelek] = Elist.field()

	def __post_init__(self):
		Entity.save(self)
