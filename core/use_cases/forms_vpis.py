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
from core.use_cases.validation_cases import Validate_kontakt


class StatusClana(str, Enum):
	ZE_VPISAN = auto()
	PONOVNO_VPISAN = auto()
	VPISAN = auto()
	ZLORABA_KONTAKTA = auto()  # Clan da številko od že obstoječega člana (možno da napačno napiše ime sebe ali skbrnika)
	ZLORABA_SKRBNIKA = auto()  # Clan da številko samega sebe !.!
	NAPAKE = auto()
	HACKER = auto()
	SKBRNIK_ZE_OBSTAJA = auto()  # 2 otroka v družini...


@dataclass
class Vpis:
	clan: Oseba
	status: StatusClana


@traced
@dataclass
class Forms_vpis(UseCase):
	db: DbService
	email: EmailService
	phone: PhoneService
	template: TemplateService
	validate_kontakt: Validate_kontakt

	async def invoke(
			self,
			ime: str, priimek: str,
			dan_rojstva: int, mesec_rojstva: int, leto_rojstva: int,
			email: str, telefon: str,
			ime_skrbnika: str = None, priimek_skrbnika: str = None,
			email_skrbnika: str = None, telefon_skrbnika: str = None) -> Vpis:

		# FORMAT PHONE
		telefon = self.phone.parse(phone=telefon)
		telefon_skrbnika = self.phone.parse(phone=telefon_skrbnika)

		# USTVARI KONTAKTE
		clan_email = Kontakt(data=email, tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN)
		clan_phone = Kontakt(data=telefon, tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN)
		skrbnik_email = Kontakt(data=email_skrbnika, tip=TipKontakta.EMAIL, validacija=TipValidacije.NI_VALIDIRAN)
		skrbnik_phone = Kontakt(data=telefon_skrbnika, tip=TipKontakta.PHONE, validacija=TipValidacije.NI_VALIDIRAN)

		# USTVARI CLANA TER GA NE VPISI NITI NE DODAJ KONTAKTOV SAJ JIH JE TREBA PREVERITI CE SE ZE PONOVIJO...
		clan = Oseba(ime=ime, priimek=priimek, tip_osebe=[TipOsebe.CLAN], rojen=date(year=leto_rojstva, month=mesec_rojstva, day=dan_rojstva))
		skrbnik = Oseba(ime=ime_skrbnika, priimek=priimek_skrbnika, tip_osebe=[TipOsebe.SKRBNIK], rojen=None)

		# PREVERI ZLORABO AUTORITETO?
		if clan.mladoletnik:
			if email == email_skrbnika or telefon == telefon_skrbnika:
				return Vpis(clan=clan, status=StatusClana.ZLORABA_SKRBNIKA)

		# CE JE UPORABNIK ZE VPISAN NE DODAJ KONTAKTOV SAJ TO NI PLAC KJER SE DODAJO KONTAKTI!!!
		with self.db.transaction(note=f'Does {clan} already exists') as root:
			raise Exception("YOU STAYED HERE")
			# TODO: You stayed here!
			# CE SE NOVI UJEMA Z STARIM IN IMA POTRJEN KONTAKT
			for old_clan in root.clan:
				if old_clan == skrbnik:
					skrbnik
				if old_clan == clan:
					if old_clan.vpisan:  # CLAN ZE VPISAN!
						return Vpis(clan=old_clan, status=StatusClana.ZE_VPISAN)
					else:  # CLAN PONOVNO VPISAN!
						old_clan.nov_vpis()
						return Vpis(clan=old_clan, status=StatusClana.PONOVNO_VPISAN)

		# ZDAJ KO IMA UPORABNIK CISTE KONTAKTE JIH LAHKO VALIDIRAMO
		self.validate_kontakt.invoke(*clan.kontakti)

		# STETJE NAPAK
		NAPAKE = len(list(filter(lambda x: not x.validiran, clan.kontakti)))
		if NAPAKE > 0:
			status = StatusClana.HACKER if NAPAKE == len(clan.kontakti) else StatusClana.NAPAKE
			return Vpis(clan=clan, status=status)

		# SHRANITEV INFORMACIJ V PODATKOVNO BAZO
		with self.db.transaction(note=f'Shrani {clan}') as root:
			root.save(clan, *clan.kontakti, unique=True)

			temp = self.template.init(ime=ime, priimek=priimek)

			await self.email.send(  # POSILJANJE POTRDITVENEGA EMAILA
				recipients=[email],
				subject=CONST.subject.vpis,
				vsebina=temp.email_vpis)

			if clan.mladoletnik:
				await self.email.send(  # POSILJANJE POTRDITVENEGA EMAILA
					recipients=[email_skrbnika],
					subject=CONST.subject.vpis_skrbnik,
					vsebina=temp.email_vpis_skrbnik)

		return validacije
