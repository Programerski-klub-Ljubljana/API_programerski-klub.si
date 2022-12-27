import json
import logging
from dataclasses import dataclass
from datetime import date
from enum import Enum, auto

from app import CONST
from core.cutils import list_field
from core.domain.arhitektura_kluba import Kontakt, TipKontakta, Oseba, NivoValidiranosti, TipOsebe
from core.services.auth_service import TokenData, AuthService
from core.services.db_service import DbService
from core.services.email_service import EmailService
from core.services.payment_service import Customer, PaymentService, Subscription, CollectionMethod, SubscriptionHistoryStatus
from core.services.phone_service import PhoneService
from core.services.vcs_service import VcsService, VcsMemberRole
from core.use_cases._usecase import UseCase
from core.use_cases.auth_cases import Send_token_parts, TokenPart
from core.use_cases.msg_cases import Poslji_porocilo_napake
from core.use_cases.validation_cases import Preveri_obstoj_kontakta

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


class TipVpisnaNapaka(str, Enum):
	VCS_INVITE_FAIL = auto()
	PAYMENT_SUBSCRIPTION_FAIL = auto()
	PAYMENT_CUSTOMER_FAIL = auto()
	IZVOR_TELEFONA_NI_NAJDEN = auto()


@dataclass
class StatusVpisa:
	clan: Oseba | None = None
	skrbnik: Oseba | None = None
	informacije: list[TipVpisnaInformacija] = list_field()
	napake: list[TipVpisnaNapaka] = list_field()


@dataclass
class VpisniPodatki:
	ime: str
	priimek: str
	dan_rojstva: int
	mesec_rojstva: int
	leto_rojstva: int
	email: str
	telefon: str
	ime_skrbnika: str | None = None
	priimek_skrbnika: str | None = None
	email_skrbnika: str | None = None
	telefon_skrbnika: str | None = None

	def clan(self, nivo_validiranosti: NivoValidiranosti):
		return Oseba(
			ime=self.ime, priimek=self.priimek, rojen=date(year=self.leto_rojstva, month=self.mesec_rojstva, day=self.dan_rojstva),
			tip_osebe=[TipOsebe.CLAN], kontakti=[
				Kontakt(data=self.email, tip=TipKontakta.EMAIL, nivo_validiranosti=nivo_validiranosti),
				Kontakt(data=self.telefon, tip=TipKontakta.PHONE, nivo_validiranosti=nivo_validiranosti)])

	def skrbnik(self, nivo_validiranosti: NivoValidiranosti):
		return Oseba(
			ime=self.ime_skrbnika, priimek=self.priimek_skrbnika, rojen=None,
			tip_osebe=[TipOsebe.SKRBNIK], kontakti=[
				Kontakt(data=self.email_skrbnika, tip=TipKontakta.EMAIL, nivo_validiranosti=nivo_validiranosti),
				Kontakt(data=self.telefon_skrbnika, tip=TipKontakta.PHONE, nivo_validiranosti=nivo_validiranosti)])

	def encode(self):
		return json.dumps(list(self.__dict__.values())).replace(' ', '')

	@staticmethod
	def decode(data: str) -> 'VpisniPodatki':
		return VpisniPodatki(*json.loads(data))


class ERROR_CLAN_JE_CHUCK_NORIS(Exception):
	pass


class ERROR_CLAN_JE_ZE_VPISAN(Exception):
	pass


class ERROR_VALIDACIJA_KONTAKTOV(Exception):
	pass


@dataclass
class Pripravi_vclanitveni_postopek(UseCase):
	preveri_obstoj_kontakta: Preveri_obstoj_kontakta
	phone: PhoneService
	email: EmailService
	auth: AuthService
	send_token_parts: Send_token_parts
	db: DbService

	async def exe(self, vp: VpisniPodatki) -> list[TokenPart] | None:
		# ! NA TEJ TOCKI KO NEVES ALI SO KONTAKTI RES UPORABNISKI NE SMES NOBENE INFORMACIJE IZDATI UPORABNIKU (HECKER)
		# ! HACKER LAHKO UPORABNI TE INFORMACIJE V ZLOBNE NAMENE!

		# * FORMATIRAJ TELEFONE
		vp.telefon = self.phone.format(phone=vp.telefon)
		vp.telefon_skrbnika = self.phone.format(phone=vp.telefon_skrbnika)

		# ! ERROR CE JE CHUCK NORIS
		if vp.email == vp.email_skrbnika or vp.telefon == vp.telefon_skrbnika:
			raise ERROR_CLAN_JE_CHUCK_NORIS()

		# * ZACNI VPISNI PROTOKOL
		clan = vp.clan(nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)
		skrbnik = vp.skrbnik(nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)

		# ! ERROR JE ZE VPISAN
		# * TUKAJ SE MERGANJE NE DELA SAJ JE LAHKO HACKER :)
		db_oseba: Oseba
		for db_oseba in self.db.find(entity=clan):
			clan = db_oseba
			if db_oseba.vpisan:
				raise ERROR_CLAN_JE_ZE_VPISAN()

		# * V PRIMERU CE SE SKRBNIK NAHAJA V BAZI NI TREBA NJEMU POSILJATI EMAIL-A
		if clan.mladoletnik:
			for db_oseba in self.db.find(entity=skrbnik):
				skrbnik = db_oseba

		# ! ERROR KONTAKT NI VALIDIRAN
		kontakti = self._preveri_obstoj_kontaktov(*clan.kontakti)
		if clan.mladoletnik:
			kontakti += self._preveri_obstoj_kontaktov(*skrbnik.kontakti)

		# * USTVARI OSNOVNI TOKEN
		token = self.auth.encode(token_data=TokenData(data=vp.encode()), expiration=CONST.auth_verification_token_life)

		# * CREATE JWT TOKEN WITH 4 PARTS
		return await self.send_token_parts.exe(token=token.data, kontakti=kontakti)

	def _preveri_obstoj_kontaktov(self, *kontakti: Kontakt) -> list[Kontakt]:
		# * NAJPREJ PREVERI EMAIL-a POTEM PA TELEFONE TAKO JE MANJ VERJETNO DA BO HACKER TI PORABLJAL PHONE MONEY
		email_kontakti = [k for k in kontakti if k.tip == TipKontakta.EMAIL]
		phone_kontakti = [k for k in kontakti if k.tip == TipKontakta.PHONE]

		validirani_kontakti = []
		for kontakt in email_kontakti + phone_kontakti:
			if kontakt.nivo_validiranosti == NivoValidiranosti.NI_VALIDIRAN:
				if self._kontakt_obstaja(kontakt=kontakt):
					kontakt.nivo_validiranosti = NivoValidiranosti.VALIDIRAN
				else:
					raise ERROR_VALIDACIJA_KONTAKTOV(kontakt)
				validirani_kontakti.append(kontakt)
		return validirani_kontakti

	def _kontakt_obstaja(self, kontakt: Kontakt):
		match kontakt.tip:
			case TipKontakta.EMAIL:
				return self.email.check_existance(email=kontakt.data)
			case TipKontakta.PHONE:
				return self.phone.check_existance(phone=kontakt.data)
		return False


class ERROR_NEVELJAVEN_TOKEN(Exception):
	pass


@dataclass
class Zacni_vclanitveni_postopek(UseCase):
	db: DbService
	phone: PhoneService
	payment: PaymentService
	vcs: VcsService
	auth: AuthService
	poslji_porocilo_napake: Poslji_porocilo_napake

	async def exe(self, token: str) -> StatusVpisa:
		# * DEKODIRAJ TOKEN
		token = self.auth.decode(token)

		# ! V PRIMERU DA SE TOKEN NE MORA DEKODIRATI TAKOJ PREKINI
		if token is None:
			raise ERROR_NEVELJAVEN_TOKEN()

		# * DEKODIRAJ TOKEN V JSONA IN GA PREVERI CE JE PRAVILNE OBLIKE?
		vp = VpisniPodatki.decode(token.d)
		status = StatusVpisa(
			clan=vp.clan(nivo_validiranosti=NivoValidiranosti.POTRJEN),
			skrbnik=vp.skrbnik(nivo_validiranosti=NivoValidiranosti.POTRJEN))

		# * USTVARI CLANA IN GA POVEZI V BAZO!
		db_oseba: Oseba
		for db_oseba in self.db.find(entity=status.clan):
			db_oseba.merge(status.clan, merge_kontakti=True, merge_vpisi_izpisi=False)
			status.clan = db_oseba

		# * USTVARI SKRBNIKA IN GA POVEZI V BAZO!
		if status.clan.mladoletnik:
			for db_oseba in self.db.find(entity=status.skrbnik):
				db_oseba.merge(status.skrbnik, merge_kontakti=True, merge_vpisi_izpisi=False)
				status.skrbnik = db_oseba

		# * CE NI BILO NAPAK USTVARI PAYMENT CUSTOMERJA
		await self._create_payment_customer(
			status=status,
			billing_phone=vp.telefon_skrbnika if status.clan.mladoletnik else vp.telefon,
			billing_email=vp.email_skrbnika if status.clan.mladoletnik else vp.email)

		# * SHRANI INFORMACIJE V BAZO
		self._shrani_v_bazo(status=status)

		# * CE IMA UPORABNIK GITHUB GA POVABI V ORGANIZACIJO SAJ JE NJEGOV EMAIL ZE VALIDIRAN
		await self._vcs_vabilo_v_organizacijo(status=status, email=vp.email)

		# ! PO KONCANEM PREVERI DB CONSISTENCY!!!
		return status

	def _create_payment_customer(self, status: StatusVpisa, billing_phone: str, billing_email: str):
		# * POISCI IZVOR BILLING TELEFONA
		izvor_telefona = self.phone.origin(phone=billing_phone)

		# * CE SE JE MERGE ZGODIL POTEM IMA ZE NASTAVLJEN ID OD STRIPE-a
		customer = self.payment.create_customer(customer=Customer(
			id=status.clan._id, name=f'{status.clan.ime} {status.clan.priimek}',
			billing_email=billing_email,
			languages=izvor_telefona.languages))

		# ! CE SE CUSTOMER NI USTVARIL NE NADALJUJ...
		if customer is None:
			status.napake.append(TipVpisnaNapaka.PAYMENT_CUSTOMER_FAIL)
			return self.poslji_porocilo_napake.exe(
				napaka="Payment service napaka", opis="Payment customer se pri včlanitvi ni mogel ustvariti!",
				clan=status.clan, billing_phone=billing_phone, billing_email=billing_email)

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
			status.napake.append(TipVpisnaNapaka.PAYMENT_SUBSCRIPTION_FAIL)
			return self.poslji_porocilo_napake.exe(
				napaka="Payment service napaka", opis="Payment subcription se pri včlanitvi ni mogla ustvariti!",
				clan=status.clan, billing_phone=billing_phone, billing_email=billing_email, customer=customer)

		status.informacije.append(TipVpisnaInformacija.NAROCEN_NA_KLUBSKO_CLANARINO)

	def _shrani_v_bazo(self, status: StatusVpisa):
		status.clan.nov_vpis()
		with self.db.transaction(note=f'Shrani {status.clan}') as root:
			root.save(status.clan, unique=True)
			if status.clan.mladoletnik:
				status.clan.connect(status.skrbnik)
				root.save(status.skrbnik, unique=True)

	def _vcs_vabilo_v_organizacijo(self, status: StatusVpisa, email: str):
		user = self.vcs.user(email=email)
		if user is None:
			return status.informacije.append(TipVpisnaInformacija.NIMA_VCS_PROFILA)

		if self.vcs.user_invite(email=email, member_role=VcsMemberRole.DIRECT_MEMBER):
			return status.informacije.append(TipVpisnaInformacija.POVABLJEN_V_VCS_ORGANIZACIJO)

		status.napake.append(TipVpisnaNapaka.VCS_INVITE_FAIL)
		return self.poslji_porocilo_napake.exe(napaka="Vcs service napaka", opis="Vcs povabilo se pri včlanitvi ni moglo poslati!", email=email)
