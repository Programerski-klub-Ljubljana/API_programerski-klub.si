import logging
from dataclasses import dataclass
from datetime import date
from enum import Enum, auto

from app import CONST
from core.cutils import list_field
from core.domain.arhitektura_kluba import Kontakt, TipKontakta, Oseba, NivoValidiranosti, TipOsebe
from core.services.db_service import DbService
from core.services.payment_service import Customer, PaymentService, Subscription, CollectionMethod
from core.services.phone_service import PhoneService
from core.use_cases._usecase import UseCase
from core.use_cases.validation_cases import Preveri_obstoj_kontakta, Poslji_test_ki_preveri_lastnistvo_kontakta

log = logging.getLogger(__name__)


class TipPrekinitveVpisa(str, Enum):
	ZE_VPISAN = auto()
	NAPAKE = auto()  # UPORABNIK JE VNESEL PODATKE KI SO SIGURNO NAPACNE.
	CHUCK_NORIS = auto()  # MUDEL JE CHUCK NORIS KER SAMO CHUCK NORIS JE LAHKO STARS SAMEMU SEBI
	# ---- When Chuck Norris was born the doctor asked him to name his parents.
	# ---- When Chuck Norris was a baby he farted for the first time, that is when the big bang first happened.
	# ---- The day after Chuck Norris was born he drove his mother home, he wanted her to get some rest.
	# ---- Chuck Norris built the hospital that he was born in.
	HACKER = auto()  # UPORABNIK JE VNESEL VSE NAPACNE PODATKE.
	NAROCNINA = auto()


@dataclass
class StatusVpisa:
	clan: Oseba | None = None
	skrbnik: Oseba | None = None
	razlogi_prekinitve: list[TipPrekinitveVpisa] = list_field()
	validirani_podatki_skrbnika: list[Kontakt] = list_field()
	validirani_podatki_clana: list[Kontakt] = list_field()

	def _napacni_podatki(self, kontakti):
		lam_ni_validiran = lambda kontakt: kontakt.nivo_validiranosti == NivoValidiranosti.NI_VALIDIRAN
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
class Zacni_vclanitveni_postopek(UseCase):
	db: DbService
	phone: PhoneService
	payment: PaymentService
	validate_kontakts_existances: Preveri_obstoj_kontakta
	validate_kontakts_ownerships: Poslji_test_ki_preveri_lastnistvo_kontakta

	async def exe(
			self,
			ime: str, priimek: str,
			dan_rojstva: int, mesec_rojstva: int, leto_rojstva: int,
			email: str, telefon: str,
			ime_skrbnika: str | None = None, priimek_skrbnika: str | None = None,
			email_skrbnika: str | None = None, telefon_skrbnika: str | None = None) -> StatusVpisa:
		# ZACNI VPISNI POSTOPEK
		vpis: StatusVpisa = StatusVpisa()

		# FORMAT PHONE
		telefon = self.phone.format(phone=telefon)

		# USTVARI CLANA
		vpis.clan = Oseba(
			ime=ime, priimek=priimek, rojen=date(year=leto_rojstva, month=mesec_rojstva, day=dan_rojstva),
			tip_osebe=[TipOsebe.CLAN], kontakti=[
				Kontakt(data=email, tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
				Kontakt(data=telefon, tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)])

		# VPISI SAMO IN SAMO CLANA! SKRBNIK SE NE STEJE KOT VPISAN ELEMENT!
		vpis.clan.nov_vpis()

		# MERGE CLAN IN DB
		db_oseba: Oseba
		for db_oseba in self.db.find(entity=vpis.clan):
			# CE JE CLAN ZE VPISAN POTEM PREKINI CELOTEN PROCES!
			if db_oseba.vpisan:
				vpis.razlogi_prekinitve.append(TipPrekinitveVpisa.ZE_VPISAN)
			db_oseba.merge(vpis.clan)
			vpis.clan = db_oseba

		if vpis.clan.mladoletnik:
			# FORMAT PHONE
			telefon_skrbnika = self.phone.format(phone=telefon_skrbnika)

			# USTVARI SKRBNIKA... KATEREGA NE VPISI!!!
			vpis.skrbnik = Oseba(
				ime=ime_skrbnika, priimek=priimek_skrbnika, rojen=None,
				tip_osebe=[TipOsebe.SKRBNIK], kontakti=[
					Kontakt(data=email_skrbnika, tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
					Kontakt(data=telefon_skrbnika, tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)])

			# PREVERI ZLORABO AUTORITETO?
			if email == email_skrbnika or telefon == telefon_skrbnika:  # Nisi chuck noris da bi bil sam seb skrbnik.
				vpis.razlogi_prekinitve.append(TipPrekinitveVpisa.CHUCK_NORIS)

			# MERGE SKRBNIK
			for db_oseba in self.db.find(entity=vpis.skrbnik):
				db_oseba.merge(vpis.skrbnik)
				vpis.skrbnik = db_oseba

		# ZDAJ KO IMA UPORABNIK CISTE KONTAKTE JIH LAHKO VALIDIRAMO
		# PAZI: CLAN IN SKRBNIK JE LAHKO MERGAN PRESTEJ SAMO TISTO KAR SE JE VALIDIRALO!
		# TODO: Ce se validacija zgodi... sli se spremembe na kontaktih shranijo v podatkovni bazi???
		vpis.validirani_podatki_clana = self.validate_kontakts_existances.exe(*vpis.clan.kontakti)
		if vpis.clan.mladoletnik:
			vpis.validirani_podatki_skrbnika = self.validate_kontakts_existances.exe(*vpis.skrbnik.kontakti)

		ST_VALIDACIJ = len(vpis.validirani_podatki)
		if vpis.stevilo_napacnih_podatkov > 0:
			vpis.razlogi_prekinitve.append(TipPrekinitveVpisa.NAPAKE)
			if vpis.stevilo_napacnih_podatkov == ST_VALIDACIJ:
				vpis.razlogi_prekinitve.append(TipPrekinitveVpisa.HACKER)

		# SE NI VPISAL IN NI BILO NAPAK
		if len(vpis.razlogi_prekinitve) == 0:

			# SHRANI CLANA IN SKRBNIKA V BAZI
			with self.db.transaction(note=f'Shrani {vpis.clan}') as root:
				root.save(vpis.clan, unique=True)
				if vpis.clan.mladoletnik:
					vpis.clan.connect(vpis.skrbnik)
					root.save(vpis.skrbnik, unique=True)
					await self.validate_kontakts_ownerships.exe(oseba=vpis.skrbnik)
				await self.validate_kontakts_ownerships.exe(oseba=vpis.clan)

			phone_origin = self.phone.origin(telefon)
			# SELE KO JE CLAN IN SKRBNIK SHRANJEN NA VARNO V MOJI BAZI USTVARIM PAYMENT FLOW ZA NJEGA
			# CE GRE PAYMENT V MALORO GA SE VEDNO LAHKO NA ROKE VPISEM
			customer = self.payment.create_customer(customer=Customer(
				name=f'{vpis.clan.ime} {vpis.clan.priimek}', phone=telefon, email=email,
				languages=phone_origin.languages, timezone=phone_origin.timezone,
				billing_emails=[email_skrbnika if vpis.clan.mladoletnik else email]))

			if customer is not None:
				vpis.clan._id = customer.id

				subscription = self.payment.create_subscription(subscription=Subscription(
					prices=[CONST.payment_prices.klubska_clanarina],
					customer=customer, collection_method=CollectionMethod.SEND_INVOICE,
					days_until_due=CONST.days_until_due, trial_period_days=CONST.trial_period_days
				))
				# TODO: You stayed here!

		return vpis
