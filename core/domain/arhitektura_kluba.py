from dataclasses import dataclass
from datetime import datetime, date
from enum import auto

from core import cutils
from core.domain._entity import elist, Elist, Entity
from core.domain._enums import EntityEnum


class TipKontakta(EntityEnum):
	EMAIL = auto()
	PHONE = auto()


class NivoValidiranosti(EntityEnum):
	NI_VALIDIRAN = auto()
	VALIDIRAN = auto()
	POTRJEN = auto()


class TipOsebe(EntityEnum):
	ADMIN = auto()
	TRENER = auto()
	CLAN = auto()
	SKRBNIK = auto()

	@classmethod
	def dovoljenja(cls):
		return {k: f'Dovoljenje za {k}' for k in TipOsebe.values()}


@dataclass
class Kontakt(Entity):
	data: str
	tip: TipKontakta
	nivo_validiranosti: NivoValidiranosti = NivoValidiranosti.NI_VALIDIRAN

	def equal(self, kontakt):
		return self.data == kontakt.data and self.tip == kontakt.tip


@dataclass
class Oseba(Entity):
	ime: str
	priimek: str
	rojen: date | None
	geslo: str | None = None
	tip_osebe: elist[TipOsebe] = Elist.field()
	kontakti: elist[Kontakt] = Elist.field()
	vpisi: elist[datetime] = Elist.field()
	izpisi: elist[datetime] = Elist.field()

	def equal(self, oseba):
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
						k1.equal(k2) and
						(k1.nivo_validiranosti == NivoValidiranosti.POTRJEN or k2.nivo_validiranosti == NivoValidiranosti.POTRJEN) and
						k1.tip == k2.tip):
					return True

		return False

	def merge(self, oseba, merge_kontakti: bool, merge_vpisi_izpisi: bool) -> bool:
		self.log_call(self.merge, kwargs=locals())

		# Save GUARD FOR STUPID DEVELOPERS!
		if not self.equal(oseba):
			return False

		# Ce skrbnik postane clan potem kot clan vnese rojstvo in se mora shraniti v skrbnika ki nima rojstvo.
		if self.rojen is None: self.rojen = oseba.rojen

		# V primeru ce ima oseba geslo potem ga shranis v starega (zelo redko se bo to zgodilo)
		if self.geslo is None: self.geslo = oseba.geslo

		# Ce skrbnik postane clan potem je potrebno dodati njegov tip notri.
		self.dodaj_tip_osebe(*oseba.tip_osebe)

		# Vse unikatne kontakte tudi nevalidirane je potrebno dodati notri, ce se kontakt duplicira potem dodas kontakt z vecjo validacijo.
		if merge_kontakti:
			self.dodaj_kontakte(*oseba.kontakti)

		if merge_vpisi_izpisi:
			# Ce uporabnik ustvari 2 clanska accounta bi zelel mergati informacije o vpisu in izpisu v enega
			for vpis in oseba.vpisi:
				if vpis not in self.vpisi:
					self.vpisi.append(vpis)

			for izpis in oseba.izpisi:
				if izpis not in self.izpisi:
					self.izpisi.append(izpis)

		return True

	def ima_kontakt(self, kontakt_data: str) -> bool:
		for kontakt in self.kontakti:
			if kontakt.data == kontakt_data and kontakt.nivo_validiranosti == NivoValidiranosti.POTRJEN:
				return True
		return False

	def dodaj_kontakte(self, *kontakti: Kontakt):
		"""If kontakt equal take that with highest validation status"""
		for kontakt in kontakti:
			exists = False
			for old_kontakt in self.kontakti:
				if kontakt.equal(old_kontakt):
					exists = True
					if kontakt.nivo_validiranosti > old_kontakt.nivo_validiranosti:
						old_kontakt.tip = kontakt.tip
			if not exists:
				self.kontakti.append(kontakt)

	def dodaj_tip_osebe(self, *statusi: TipOsebe):
		for status in statusi:
			if status not in self.tip_osebe:
				self.tip_osebe.append(status)

	def nov_vpis(self):
		if not self.vpisan:
			self.vpisi.append(datetime.now())

	def nov_izpis(self):
		if self.vpisan:
			self.izpisi.append(datetime.now())

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
		if len(self.izpisi) == 0 or len(self.vpisi) == 0:
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


@dataclass
class Oddelek(Entity):
	ime: str
	opis: str
	ekipe: elist[Ekipa] = Elist.field()


@dataclass
class Klub(Entity):
	ime: str
	clanarina: float
	oddelki: elist[Oddelek] = Elist.field()
