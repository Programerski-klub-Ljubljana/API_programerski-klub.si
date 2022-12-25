import logging
from dataclasses import dataclass
from datetime import date
from enum import Enum, auto

from app import CONST
from core.cutils import list_field
from core.domain.arhitektura_kluba import Kontakt, TipKontakta, Oseba, NivoValidiranosti, TipOsebe
from core.services.db_service import DbService
from core.services.payment_service import Customer, PaymentService, Subscription, CollectionMethod, SubscriptionHistoryStatus
from core.services.phone_service import PhoneService
from core.services.vcs_service import VcsService, VcsMemberRole
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


class TipVpisnaInformacija(str, Enum):
	NIMA_VCS_PROFILA = auto()
	POVABLJEN_V_VCS_ORGANIZACIJO = auto()
	NAROCEN_NA_KLUBSKO_CLANARINO = auto()
	POSKUSNO_OBDOBJE = auto()
	SKRBNIK_SE_PONOVNO_VPISUJE = auto()
	MLADOLETNIK = auto()
	CLAN_SE_PONOVNO_VPISUJE = auto()


class TipVpisnoOpozorilo(str, Enum):
	VCS_INVITE_FAIL = auto()
	PAYMENT_SUBSCRIPTION_FAIL = auto()
	PAYMENT_CUSTOMER_FAIL = auto()
	IZVOR_TELEFONA_NI_NAJDEN = auto()


@dataclass
class StatusVpisa:
	clan: Oseba | None = None
	skrbnik: Oseba | None = None
	razlogi_prekinitve: list[TipPrekinitveVpisa] = list_field()
	validirani_podatki_skrbnika: list[Kontakt] = list_field()
	validirani_podatki_clana: list[Kontakt] = list_field()
	informacije: list[TipVpisnaInformacija] = list_field()
	napake: list[TipVpisnoOpozorilo] = list_field()

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
	vcs: VcsService
	validate_kontakts_existances: Preveri_obstoj_kontakta
	validate_kontakts_ownerships: Poslji_test_ki_preveri_lastnistvo_kontakta

	async def exe(
			self,
			ime: str, priimek: str,
			dan_rojstva: int, mesec_rojstva: int, leto_rojstva: int,
			email: str, telefon: str,
			ime_skrbnika: str | None = None, priimek_skrbnika: str | None = None,
			email_skrbnika: str | None = None, telefon_skrbnika: str | None = None) -> StatusVpisa:
		# * ZACNI VPISNI POSTOPEK
		status: StatusVpisa = StatusVpisa()

		# * USTVARI CLANA
		telefon = self.phone.format(phone=telefon)
		status.clan = Oseba(
			ime=ime, priimek=priimek, rojen=date(year=leto_rojstva, month=mesec_rojstva, day=dan_rojstva),
			tip_osebe=[TipOsebe.CLAN], kontakti=[
				Kontakt(data=email, tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
				Kontakt(data=telefon, tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)])

		# * USTVARI SKRBNIKA
		if status.clan.mladoletnik:
			status.informacije.append(TipVpisnaInformacija.MLADOLETNIK)
			telefon_skrbnika = self.phone.format(phone=telefon_skrbnika)
			status.skrbnik = Oseba(
				ime=ime_skrbnika, priimek=priimek_skrbnika, rojen=None,
				tip_osebe=[TipOsebe.SKRBNIK], kontakti=[
					Kontakt(data=email_skrbnika, tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
					Kontakt(data=telefon_skrbnika, tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)])

			if email == email_skrbnika or telefon == telefon_skrbnika:  # Nisi chuck noris da bi bil sam seb skrbnik.
				status.razlogi_prekinitve.append(TipPrekinitveVpisa.CHUCK_NORIS)

		# * PREPARE OSEBE ZA VPIS
		self._merge_osebe(status=status)
		self._validacija_kontaktov(status=status)

		# ! V PRIMERU NAPAK PREKINI VPISNI POSTOPEK
		if len(status.razlogi_prekinitve) > 0:
			return status

		# * CE NI BILO NAPAK USTVARI PAYMENT CUSTOMERJA
		self._create_payment_customer(
			status=status, billing_phone=telefon_skrbnika if status.clan.mladoletnik else telefon,
			billing_email=email_skrbnika if status.clan.mladoletnik else email)

		# * SHRANI INFORMACIJE V BAZO
		self._shrani_v_bazo(status=status)

		# * PREVERI OVNERSHIP ZA KONTAKTE
		await self._validate_kontakts_ownerships(status=status)

		# * CE IMA UPORABNIK GITHUB GA POVABI V ORGANIZACIJO SAJ JE NJEGOV EMAIL ZE VALIDIRAN
		self._vcs_vabilo_v_organizacijo(status=status, email=email)

		return status

	def _merge_osebe(self, status: StatusVpisa):
		db_oseba: Oseba  # Type hinting...

		# * V PRIMERU CE SE CLAN NAHAJA V BAZI
		for db_oseba in self.db.find(entity=status.clan):
			status.informacije.append(TipVpisnaInformacija.CLAN_SE_PONOVNO_VPISUJE)
			# CE JE CLAN ZE VPISAN POTEM PREKINI CELOTEN PROCES!
			if db_oseba.vpisan:
				status.razlogi_prekinitve.append(TipPrekinitveVpisa.ZE_VPISAN)
			db_oseba.merge(status.clan)
			status.clan = db_oseba

		# * V PRIMERU CE SE SKRBNIK NAHAJA V BAZI
		if status.clan.mladoletnik:
			for db_oseba in self.db.find(entity=status.skrbnik):
				status.informacije.append(TipVpisnaInformacija.SKRBNIK_SE_PONOVNO_VPISUJE)
				db_oseba.merge(status.skrbnik)
				status.skrbnik = db_oseba

	def _validacija_kontaktov(self, status: StatusVpisa):
		# * PREVERI KONTAKTE CLANA
		status.validirani_podatki_clana = self.validate_kontakts_existances.exe(*status.clan.kontakti)

		# * PREVERI KONTAKTE SKRBNIKA
		if status.clan.mladoletnik:
			status.validirani_podatki_skrbnika = self.validate_kontakts_existances.exe(*status.skrbnik.kontakti)

		# * PREVERI STEVILO NAPAK
		ST_VALIDACIJ = len(status.validirani_podatki)
		if status.stevilo_napacnih_podatkov > 0:
			status.razlogi_prekinitve.append(TipPrekinitveVpisa.NAPAKE)
			if status.stevilo_napacnih_podatkov == ST_VALIDACIJ:
				status.razlogi_prekinitve.append(TipPrekinitveVpisa.HACKER)

	def _create_payment_customer(self, status: StatusVpisa, billing_phone: str, billing_email: str):
		# * POISCI IZVOR BILLING TELEFONA
		izvor_telefona = self.phone.origin(phone=billing_phone)
		if len(izvor_telefona.languages) == 0:
			status.napake.append(TipVpisnoOpozorilo.IZVOR_TELEFONA_NI_NAJDEN)

		# * CE SE JE MERGE ZGODIL POTEM IMA ZE NASTAVLJEN ID OD STRIPE-a
		customer = self.payment.create_customer(customer=Customer(
			id=status.clan._id, name=f'{status.clan.ime} {status.clan.priimek}',
			billing_email=billing_email,
			languages=izvor_telefona.languages))

		# ! CE SE CUSTOMER NI USTVARIL NE NADALJUJ...
		if customer is None:
			return status.napake.append(TipVpisnoOpozorilo.PAYMENT_CUSTOMER_FAIL)

		# * OBVEZNA POSODOBITEV ID KI SE UJEMA Z PAYMENT ID
		status.clan._id = customer.id

		# * PREVERI ZGODOVINO SUBSCRIPTIONS
		sub_history_status = customer.subscription_history_status(price=CONST.payment_prices.klubska_clanarina)
		trial_period_days = 0
		match sub_history_status:

			# * CE SE NI BIL NIKOLI NAROCEN
			case SubscriptionHistoryStatus.NEVER_SUBSCRIBED:
				status.informacije.append(TipVpisnaInformacija.POSKUSNO_OBDOBJE)
				trial_period_days = CONST.trial_period_days

		# * CE NI ZE NAROCEN POTEM USTVARI SUBSCRIPTION NA KLUBSKO CLANARINO
		subscription = self.payment.create_subscription(subscription=Subscription(
			prices=[CONST.payment_prices.klubska_clanarina],
			customer=customer, collection_method=CollectionMethod.SEND_INVOICE,
			days_until_due=CONST.days_until_due, trial_period_days=trial_period_days))

		# ! CE SE SUBSCRIPTION NI MORALA USTVARITI POTEM KONCAJ...
		if subscription is None:
			return status.napake.append(TipVpisnoOpozorilo.PAYMENT_SUBSCRIPTION_FAIL)

		status.informacije.append(TipVpisnaInformacija.NAROCEN_NA_KLUBSKO_CLANARINO)

	def _shrani_v_bazo(self, status: StatusVpisa):
		status.clan.nov_vpis()
		with self.db.transaction(note=f'Shrani {status.clan}') as root:
			root.save(status.clan, unique=True)
			if status.clan.mladoletnik:
				status.clan.connect(status.skrbnik)
				root.save(status.skrbnik, unique=True)

	async def _validate_kontakts_ownerships(self, status: StatusVpisa):
		await self.validate_kontakts_ownerships.exe(oseba=status.clan)
		if status.clan.mladoletnik:
			await self.validate_kontakts_ownerships.exe(oseba=status.skrbnik)

	def _vcs_vabilo_v_organizacijo(self, status: StatusVpisa, email: str):
		user = self.vcs.user(email=email)
		if user is None:
			return status.informacije.append(TipVpisnaInformacija.NIMA_VCS_PROFILA)

		if self.vcs.user_invite(email=email, member_role=VcsMemberRole.DIRECT_MEMBER):
			return status.informacije.append(TipVpisnaInformacija.POVABLJEN_V_VCS_ORGANIZACIJO)

		return status.napake.append(TipVpisnoOpozorilo.VCS_INVITE_FAIL)
