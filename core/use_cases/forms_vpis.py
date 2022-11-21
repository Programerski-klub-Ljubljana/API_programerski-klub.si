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
class Vpis:
	clan: Oseba | None
	skrbnik: Oseba = None
	razlogi_duplikacije_skrbnika: list[RazlogDuplikacije] = None
	razlogi_duplikacije_clana: list[RazlogDuplikacije] = None
	razlogi_prekinitve: list[TipProblema] = None
	napacni_podatki_skrbnika: list[Kontakt] = None
	napacni_podatki_clana: list[Kontakt] = None

	def __post_init__(self):
		self.razlogi_duplikacije_clana = []
		self.razlogi_duplikacije_skrbnika = []
		self.razlogi_prekinitve = []
		self.napacni_podatki_skrbnika = []
		self.napacni_podatki_clana = []

	def stevilo_napacnih_podatkov(self):
		return len(self.napacni_podatki_skrbnika + self.napacni_podatki_clana)

	def stevilo_problemov(self):
		return len(self.razlogi_prekinitve)


@traced
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
			email_skrbnika: str = None, telefon_skrbnika: str = None) -> Vpis:
		# FORMAT PHONE
		telefon = self.phone.format(phone=telefon)
		clan = Oseba(
			ime=ime, priimek=priimek, rojen=date(year=leto_rojstva, month=mesec_rojstva, day=dan_rojstva),
			tip_osebe=[TipOsebe.CLAN], kontakti=[
				Kontakt(data=email, tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN),
				Kontakt(data=telefon, tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN)])

		# ZACNI VPISNI POSTOPEK
		vpis = Vpis(clan=clan)

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
		validirani_kontaki_clana = self.validate_kontakt.invoke(*clan.kontakti)
		validirani_kontaki_skrbnika = [] if not clan.mladoletnik else self.validate_kontakt.invoke(*skrbnik.kontakti)

		ST_VALIDACIJ = len(validirani_kontaki_skrbnika + validirani_kontaki_clana)

		lam_ni_validiran = lambda kontakt: not kontakt.validacija == TipValidacije.NI_VALIDIRAN
		vpis.napacni_podatki_clana += list(filter(lam_ni_validiran, validirani_kontaki_clana))
		vpis.napacni_podatki_skrbnika += list(filter(lam_ni_validiran, validirani_kontaki_skrbnika))
		ST_NAPAK = vpis.stevilo_napacnih_podatkov()

		if ST_NAPAK > 0:
			vpis.razlogi_prekinitve.append(TipProblema.NAPAKE)
			if ST_NAPAK == ST_VALIDACIJ:
				vpis.razlogi_prekinitve.append(TipProblema.HACKER)

		# CE NI BILO NAPAK...
		if len(vpis.razlogi_prekinitve) == 0:
			# PRIPRAVI TEMPLATE
			temp = self.template.init(
				ime=ime, priimek=priimek,
				ime_skrbnika=ime_skrbnika, priimek_skrbnika=priimek_skrbnika,

				email=email, telefon=telefon,
				email_skrbnika=email_skrbnika, telefon_skrbnika=telefon_skrbnika,

				auth_verify_url=CONST.auth_verify_url,
				sms_token=self.auth_verification_token.invoke(telefon),
				email_token=self.auth_verification_token.invoke(email),
				sms_token_skrbnik=self.auth_verification_token.invoke(telefon_skrbnika),
				email_token_skrbnik=self.auth_verification_token.invoke(email_skrbnika),
			)

			# SHRANI CLANA IN SKRBNIKA
			# TODO: POSLJI EMAIL SAMO VALIDIRANIM IN NEPOTRJENIM KONTAKTOM!!!
			with self.db.transaction(note=f'Shrani {clan}') as root:
				root.save(clan)
				self.phone.sms(phone=telefon, text=temp.sms_verifikaija_clana)
				await self.email.send(  # POSILJANJE POTRDITVENEGA EMAILA
					recipients=[email],
					subject=CONST.subject.vpis,
					vsebina=temp.email_verifikacija_clana)

				if clan.mladoletnik:
					clan.povezi(skrbnik)
					root.save(skrbnik)
					self.phone.sms(phone=telefon_skrbnika, text=temp.sms_verifikaija_skrbnika)
					await self.email.send(  # POSILJANJE POTRDITVENEGA EMAILA
						recipients=[email_skrbnika],
						subject=CONST.subject.vpis_skrbnik,
						vsebina=temp.email_vpis_skrbnik)

		return vpis
