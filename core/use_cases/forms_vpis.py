import logging
from dataclasses import dataclass
from datetime import date
from enum import Enum, auto

from core.cutils import list_field
from core.domain.arhitektura_kluba import Kontakt, TipKontakta, Oseba, TipValidacije, TipOsebe
from core.services.db_service import DbService
from core.services.phone_service import PhoneService
from core.use_cases._usecase import UseCase
from core.use_cases.validation_cases import Validate_kontakts_existances, Validate_kontakts_ownerships

log = logging.getLogger(__name__)


class TipProblema(str, Enum):
	NAPAKE = auto()  # UPORABNIK JE VNESEL PODATKE KI SO SIGURNO NAPACNE.
	CHUCK_NORIS = auto()  # MUDEL JE CHUCK NORIS KER SAMO CHUCK NORIS JE LAHKO STARS SAMEMU SEBI
	# ---- When Chuck Norris was born the doctor asked him to name his parents.
	# ---- When Chuck Norris was a baby he farted for the first time, that is when the big bang first happened.
	# ---- The day after Chuck Norris was born he drove his mother home, he wanted her to get some rest.
	# ---- Chuck Norris built the hospital that he was born in.
	HACKER = auto()  # UPORABNIK JE VNESEL VSE NAPACNE PODATKE.


@dataclass
class StatusVpisa:
	clan: Oseba | None = None
	skrbnik: Oseba | None = None
	razlogi_prekinitve: list[TipProblema] = list_field()
	validirani_podatki_skrbnika: list[Kontakt] = list_field()
	validirani_podatki_clana: list[Kontakt] = list_field()

	def _napacni_podatki(self, kontakti):
		lam_ni_validiran = lambda kontakt: kontakt.validacija == TipValidacije.NI_VALIDIRAN
		return list(filter(lam_ni_validiran, kontakti))

	@property
	def napacni_podatki_skrbnika(self):
		return self._napacni_podatki(self.validirani_podatki_skrbnika)

	@property
	def napacni_podatki_clana(self):
		return self._napacni_podatki(self.validirani_podatki_clana)

	@property
	def stevilo_napacnih_podatkov(self):
		return len(self.napacni_podatki_skrbnika + self.napacni_podatki_clana)

	@property
	def validirani_podatki(self):
		return self.validirani_podatki_skrbnika + self.validirani_podatki_clana

	@property
	def stevilo_problemov(self):
		return len(self.razlogi_prekinitve)

	def __str__(self):
		return f"""
			Clan   : {self.clan}
			Skrbnik: {self.skrbnik}
			Razlogi prekinitve          : {self.razlogi_prekinitve}
			Napake skrbnika: {", ".join(k.data for k in self.napacni_podatki_skrbnika)}
			Napake clana   : {", ".join(k.data for k in self.napacni_podatki_clana)}
		""".removeprefix('\t\t')


@dataclass
class Forms_vpis(UseCase):
	db: DbService
	phone: PhoneService
	validate_kontakts_existances: Validate_kontakts_existances
	validate_kontakts_ownerships: Validate_kontakts_ownerships

	async def invoke(
			self,
			ime: str, priimek: str,
			dan_rojstva: int, mesec_rojstva: int, leto_rojstva: int,
			email: str, telefon: str,
			ime_skrbnika: str | None = None, priimek_skrbnika: str | None = None,
			email_skrbnika: str | None = None, telefon_skrbnika: str | None = None) -> StatusVpisa:
		kwargs = locals()
		del kwargs['self']

		# ZACNI VPISNI POSTOPEK
		vpis: StatusVpisa = StatusVpisa()

		# FORMAT PHONE
		telefon = self.phone.format(phone=telefon)

		# USTVARI CLANA
		vpis.clan = Oseba(
			ime=ime, priimek=priimek, rojen=date(year=leto_rojstva, month=mesec_rojstva, day=dan_rojstva),
			tip_osebe=[TipOsebe.CLAN], kontakti=[
				Kontakt(data=email, tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN),
				Kontakt(data=telefon, tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN)])

		# VPISI CLANA
		vpis.clan.nov_vpis()

		# MERGE CLAN
		oseba: Oseba
		for oseba in self.db.find(entity=vpis.clan):
			oseba.merge(vpis.clan)
			vpis.clan = oseba

		if vpis.clan.mladoletnik:
			# FORMAT PHONE
			telefon_skrbnika = self.phone.format(phone=telefon_skrbnika)

			# USTVARI SKRBNIKA... KATEREGA NE VPISI!!!
			vpis.skrbnik = Oseba(
				ime=ime_skrbnika, priimek=priimek_skrbnika, rojen=None,
				tip_osebe=[TipOsebe.SKRBNIK], kontakti=[
					Kontakt(data=email_skrbnika, tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN),
					Kontakt(data=telefon_skrbnika, tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN)])

			# PREVERI ZLORABO AUTORITETO?
			if email == email_skrbnika or telefon == telefon_skrbnika:  # Nisi chuck noris da bi bil sam seb skrbnik.
				vpis.razlogi_prekinitve.append(TipProblema.CHUCK_NORIS)

			# MERGE SKRBNIK
			for oseba in self.db.find(entity=vpis.clan):
				oseba.merge(vpis.clan)
				vpis.skrbnik = oseba

		# ZDAJ KO IMA UPORABNIK CISTE KONTAKTE JIH LAHKO VALIDIRAMO
		# PAZI: CLAN IN SKRBNIK JE LAHKO MERGAN PRESTEJ SAMO TISTO KAR SE JE VALIDIRALO!
		vpis.validirani_podatki_clana = self.validate_kontakts_existances.invoke(*vpis.clan.kontakti)
		if vpis.clan.mladoletnik:
			vpis.validirani_podatki_skrbnika = self.validate_kontakts_existances.invoke(*vpis.skrbnik.kontakti)

		ST_VALIDACIJ = len(vpis.validirani_podatki)
		ST_NAPAK = vpis.stevilo_napacnih_podatkov
		if ST_NAPAK > 0:
			vpis.razlogi_prekinitve.append(TipProblema.NAPAKE)
			if ST_NAPAK == ST_VALIDACIJ:
				vpis.razlogi_prekinitve.append(TipProblema.HACKER)

		# CE NI BILO NAPAK...
		if len(vpis.razlogi_prekinitve) == 0:

			# SHRANI CLANA IN SKRBNIKA
			with self.db.transaction(note=f'Shrani {vpis.clan}') as root:
				root.save(vpis.clan, unique=True)
				if vpis.clan.mladoletnik:
					vpis.clan.povezi(vpis.skrbnik)
					root.save(vpis.skrbnik, unique=True)
					await self.validate_kontakts_ownerships.invoke(oseba=vpis.skrbnik)
				await self.validate_kontakts_ownerships.invoke(oseba=vpis.clan)

		return vpis
