import logging
from dataclasses import dataclass
from datetime import date
from enum import Enum, auto

from autologging import traced

from app import CONST
from core.domain.arhitektura_kluba import Kontakt, TipKontakta, Oseba, TipValidacije, TipOsebe
from core.services.db_service import DbService
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.services.template_service import TemplateService
from core.use_cases._usecase import UseCase
from core.use_cases.auth_cases import Auth_verification_token
from core.use_cases.validation_cases import Validate_kontakt

log = logging.getLogger(__name__)


class RazlogDuplikacije(str, Enum):
	CLAN_POSTAJA_SKRBNIK = auto()
	ZE_VPISAN = auto()  # SKRBNIK ALI CLAN
	PONOVNO_VPISAN = auto()  # SKRBNIK ALI CLAN
	SKRBNIK_POSTAJA_CLAN = auto()  # NAVDUŠEN SKRBNIK POSTAJA CLAN!
	ZE_IMA_VAROVANCA = auto()  # SKRBNIK IMA ZE ENEGA VAROVANCA ZDAJ SE PA SE PRIJAVLJA DRUGI.


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
	clan: Oseba | None
	skrbnik: Oseba = None
	razlogi_duplikacije_skrbnika: list[RazlogDuplikacije] = None
	razlogi_duplikacije_clana: list[RazlogDuplikacije] = None
	razlogi_prekinitve: list[TipProblema] = None
	validirani_podatki_skrbnika: list[Kontakt] = None
	validirani_podatki_clana: list[Kontakt] = None

	def __post_init__(self):
		self.razlogi_duplikacije_clana = []
		self.razlogi_duplikacije_skrbnika = []
		self.razlogi_prekinitve = []
		self.validirani_podatki_clana = []
		self.validirani_podatki_skrbnika = []

	def _napacni_podatki(self, kontakti):
		lam_ni_validiran = lambda kontakt: kontakt.validacija == TipValidacije.NI_VALIDIRAN
		return list(filter(lam_ni_validiran, kontakti))

	@property
	def napacni_podatki_skrbnika(self):
		return self._napacni_podatki(self.validirani_podatki_skrbnika)

	@property
	def napacni_podatki_clana(self):
		return self._napacni_podatki(self.validirani_podatki_clana)

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
			Razlogi duplikacije skrbnika: {self.razlogi_duplikacije_skrbnika}
			Razlogi duplikacije clana   : {self.razlogi_duplikacije_clana}
			Razlogi prekinitve          : {self.razlogi_prekinitve}
			Napake skrbnika: {", ".join(k.token_data for k in self.napacni_podatki_skrbnika)}
			Napake clana   : {", ".join(k.token_data for k in self.napacni_podatki_clana)}
		""".removeprefix('\t\t')


@dataclass
class Forms_vpis(UseCase):
	db: DbService
	email: EmailService
	phone: PhoneService
	template: TemplateService
	validate_kontakt: Validate_kontakt
	auth_verification_token: Auth_verification_token

	async def invoke(
			self,
			ime: str, priimek: str,
			dan_rojstva: int, mesec_rojstva: int, leto_rojstva: int,
			email: str, telefon: str,
			ime_skrbnika: str = None, priimek_skrbnika: str = None,
			email_skrbnika: str = None, telefon_skrbnika: str = None) -> StatusVpisa:
		kwargs = locals()
		del kwargs['self']

		# FORMAT PHONE
		telefon = self.phone.format(phone=telefon)
		clan = Oseba(
			ime=ime, priimek=priimek, rojen=date(year=leto_rojstva, month=mesec_rojstva, day=dan_rojstva),
			tip_osebe=[TipOsebe.CLAN], kontakti=[
				Kontakt(data=email, tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN),
				Kontakt(data=telefon, tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN)])

		# ZACNI VPISNI POSTOPEK
		vpis = StatusVpisa(clan=clan)

		skrbnik = None
		if clan.mladoletnik:
			telefon_skrbnika = self.phone.format(phone=telefon_skrbnika)
			skrbnik = Oseba(
				ime=ime_skrbnika, priimek=priimek_skrbnika, rojen=None,
				tip_osebe=[TipOsebe.SKRBNIK], kontakti=[
					Kontakt(data=email_skrbnika, tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN),
					Kontakt(data=telefon_skrbnika, tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN)])

			vpis.skrbnik = skrbnik
			# PREVERI ZLORABO AUTORITETO?
			if email == email_skrbnika or telefon == telefon_skrbnika:  # Nisi chuck noris da bi bil sam seb skrbnik.
				vpis.razlogi_prekinitve.append(TipProblema.CHUCK_NORIS)

		# PREVERI MOZNO DUPLIKACIJO PODATKOV!
		with self.db.transaction(note=f'Merge {clan} or {skrbnik} if already exists') as root:
			for old_oseba in root.oseba:

				# LOGIKA CE SKRBNIK OBSTAJA ALI PA ZE OBSTAJA..
				if skrbnik is not None:
					if old_oseba == skrbnik:
						if old_oseba.vpisan:
							vpis.razlogi_duplikacije_skrbnika.append(RazlogDuplikacije.ZE_VPISAN)  # ALI JE ZE VPISAN
						if TipOsebe.SKRBNIK in old_oseba.tip_osebe:  # SKRBNIK JE ZE SKRBNIK DRUGEGA CLANA
							vpis.razlogi_duplikacije_skrbnika.append(RazlogDuplikacije.ZE_IMA_VAROVANCA)
						if TipOsebe.CLAN in old_oseba.tip_osebe:  # CLAN POSTAJA SKRBNIK TEMU VAROVANCU
							vpis.razlogi_duplikacije_skrbnika.append(RazlogDuplikacije.CLAN_POSTAJA_SKRBNIK)

						# MERGING OLD WITH NEW
						old_oseba.dodaj_kontakte(*skrbnik.kontakti)  # MERGAJ SVEZE KONTAKTE CE OBSTAJAJO
						old_oseba.dodaj_tip_osebe(*skrbnik.statusi)  # MERGAJ STATUSE!
						skrbnik = old_oseba  # UPORABI STARO OSEBO KI ZE OBSTAJA DA PREPRECIS DUPLIKATE V BAZI

				# LOGIKA CE CLAN ZE OBSTAJA...
				if old_oseba == clan:
					if old_oseba.vpisan:
						vpis.razlogi_duplikacije_clana.append(RazlogDuplikacije.ZE_VPISAN)  # ALI JE ZE VPISAN
					if TipOsebe.SKRBNIK in old_oseba.tip_osebe:  # SKBRNIK JE PRIJAVIL SINA V PRETEKLOSTI ZDAJ PA SE ON VSTOPA V KLUB
						vpis.razlogi_duplikacije_clana.append(RazlogDuplikacije.SKRBNIK_POSTAJA_CLAN)
					if TipOsebe.CLAN in old_oseba.tip_osebe:  # CLAN SE JE V PRETEKLOSTI IZPISAL ZDAJ SE PA VPISUJE NAZAJ
						old_oseba.nov_vpis()
						vpis.razlogi_duplikacije_clana.append(RazlogDuplikacije.PONOVNO_VPISAN)

					# MERGING OLD WITH NEW
					old_oseba.dodaj_kontakte(*clan.kontakti)  # MERGAJ SVEZE KONTAKTE CE OBSTAJAJO
					old_oseba.dodaj_tip_osebe(*clan.statusi)  # MERGAJ STATUSE!
					clan = old_oseba  # UPORABI STARO OSEBO KI ZE OBSTAJA DA PREPRECIS DUPLIKATE V BAZI

		# ZDAJ KO IMA UPORABNIK CISTE KONTAKTE JIH LAHKO VALIDIRAMO
		# PAZI: CLAN IN SKRBNIK JE LAHKO MERGAN PRESTEJ SAMO TISTO KAR SE JE VALIDIRALO!
		vpis.validirani_kontaki_clana = self.validate_kontakt.invoke(*clan.kontakti)
		if clan.mladoletnik:
			vpis.validirani_podatki_skrbnika = self.validate_kontakt.invoke(*skrbnik.kontakti)

		ST_VALIDACIJ = len(vpis.validirani_podatki)
		ST_NAPAK = vpis.stevilo_napacnih_podatkov()
		if ST_NAPAK > 0:
			vpis.razlogi_prekinitve.append(TipProblema.NAPAKE)
			if ST_NAPAK == ST_VALIDACIJ:
				vpis.razlogi_prekinitve.append(TipProblema.HACKER)

		# CE NI BILO NAPAK...
		if len(vpis.razlogi_prekinitve) == 0:

			# SHRANI CLANA IN SKRBNIKA
			with self.db.transaction(note=f'Shrani {clan}') as root:
				root.save(clan)

				# PRIPRAVI TEMPLATE
				temp = self.template.init(
					**kwargs,
					sms_token=self.auth_verification_token.invoke(telefon).data,
					email_token=self.auth_verification_token.invoke(email).data,
					sms_token_skrbnik=self.auth_verification_token.invoke(telefon_skrbnika).data,
					email_token_skrbnik=self.auth_verification_token.invoke(email_skrbnika).data)

				# POJDI PO KONTAKTIH IN POSLJI NEPOTRJENIM KONTAKTOM VALIDACIJSKE SPOROCILA
				for kontakt in clan.kontakti:
					if kontakt.validacija == TipValidacije.VALIDIRAN:
						if kontakt.tip == TipKontakta.EMAIL:
							await self.email.send(recipients=[email], subject=CONST.email_subject.vpis, vsebina=temp.email_verifikacija_clan)
						elif kontakt.tip == TipKontakta.PHONE:
							self.phone.sms(phone=telefon, text=temp.sms_verifikacija_clan)

				if clan.mladoletnik:
					clan.povezi(skrbnik)
					root.save(skrbnik)
					for kontakt in skrbnik.kontakti:
						if kontakt.validacija == TipValidacije.VALIDIRAN:
							if kontakt.tip == TipKontakta.EMAIL:
								await self.email.send(
									recipients=[email_skrbnika], subject=CONST.email_subject.vpis_skrbnik, vsebina=temp.email_vpis_skrbnik)
							elif kontakt.tip == TipKontakta.PHONE:
								self.phone.sms(phone=telefon_skrbnika, text=temp.sms_verifikaija_skrbnik)

		return vpis
