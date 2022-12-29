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

log = logging.getLogger(__name__)


class ERROR:
	class VPISNI_PODATKI_DECODE(Exception): pass

	class VALIDACIJA_PODATKOV(Exception): pass

	class CLAN_JE_CHUCK_NORIS(Exception): pass

	class CLAN_JE_ZE_VPISAN(Exception): pass

	class VALIDACIJA_KONTAKTOV(Exception): pass

	class NEVELJAVEN_TOKEN(Exception): pass


class TipVpisnaInformacija(str, Enum):
	CLAN_JE_MLADOLETNIK = auto()
	NIMA_VCS_PROFILA = auto()
	POVABLJEN_V_VCS_ORGANIZACIJO = auto()
	NAROCEN_NA_KLUBSKO_CLANARINO = auto()
	POSKUSNO_OBDOBJE = auto()
	SKRBNIK_SE_PONOVNO_VPISUJE = auto()
	CLAN_SE_PONOVNO_VPISUJE = auto()


class TipVpisnaNapaka(str, Enum):
	CLAN_JE_VPISAN = auto()
	PAYMENT_CUSTOMER_IS_SUBSCRIBED = auto()
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
	def decode(data: str) -> 'VpisniPodatki | None':
		try:
			return VpisniPodatki(*json.loads(data))
		except Exception as err:
			log.error(err)


@dataclass
class Pripravi_vclanitveni_postopek(UseCase):
	phone: PhoneService
	email: EmailService
	auth: AuthService
	send_token_parts: Send_token_parts
	db: DbService

	async def exe(self, vp: VpisniPodatki) -> list[TokenPart] | None:
		"""
			Cim manj informacij izdaj tukaj, in ne bodi prevec strog glede uporabe kontaktov.
			Bolje je da uporabnikom vec pustis in potem naknadno detektiras anomalije v db-ju,
			v nasprotnem primeru ce bos prevec strog bo folk uporabljal lahko lazna imena in kontakte,
			ce jih sistem ne bo naprej pustil kar pa nocem. Anomalije se bodo prej zaznale
			ce bos vec dovolil saj se potem heckerji ne bodo prevec trudili.
		"""

		# * FORMATIRAJ TELEFONE
		vp.telefon = self.phone.format(phone=vp.telefon)
		vp.telefon_skrbnika = self.phone.format(phone=vp.telefon_skrbnika)

		# ! ERROR CE JE CHUCK NORIS
		if vp.email == vp.email_skrbnika or vp.telefon == vp.telefon_skrbnika:
			raise ERROR.CLAN_JE_CHUCK_NORIS()

		# * ZACNI VPISNI PROTOKOL
		clan = vp.clan(nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)
		skrbnik = vp.skrbnik(nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)

		# ! ERROR JE ZE VPISAN
		db_oseba: Oseba
		for db_oseba in self.db.find(entity=clan):
			if db_oseba.vpisan:
				raise ERROR.CLAN_JE_ZE_VPISAN()

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
					raise ERROR.VALIDACIJA_KONTAKTOV(kontakt)
				validirani_kontakti.append(kontakt)
		return validirani_kontakti

	def _kontakt_obstaja(self, kontakt: Kontakt):
		match kontakt.tip:
			case TipKontakta.EMAIL:
				return self.email.check_existance(email=kontakt.data)
			case TipKontakta.PHONE:
				return self.phone.check_existance(phone=kontakt.data)
		return False


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
			raise ERROR.NEVELJAVEN_TOKEN()

		# * DEKODIRAJ TOKEN V JSONA IN GA PREVERI CE JE PRAVILNE OBLIKE?
		vp = VpisniPodatki.decode(token.d)

		# ! V PRIMERU DA SE VPISNI TOKEN NE MORA DEKODIRATI
		if vp is None:
			raise ERROR.VPISNI_PODATKI_DECODE()

		# ? NA TEJ TOCKI SE VALIDACIJA KONCA IN SE CELOTEN POSTOPEK MORA NAREDITI PA CEPRAV Z NAPAKAMI
		# ? NAPAKE SE BODO RESEVALE NA ROKO!

		# * USTVARI STATUS ZA VPIS
		status = StatusVpisa(clan=vp.clan(nivo_validiranosti=NivoValidiranosti.POTRJEN))  # * Kontakti so ze potrjeni v 1 koraku.
		if status.clan.mladoletnik:  # * CE JE MLADOLETNIK USTVARI SE SKRBNIKA
			status.skrbnik = vp.skrbnik(nivo_validiranosti=NivoValidiranosti.POTRJEN)  # * Kontakti so ze potrjeni v 1 koraku.

		# * MERGE CLANA IN SKRBNIKA SAJ MORA CLAN IZ STATUSA PRIDOBITI PRAVILEN ID ZA PAYMENT!
		self._merge_clana_in_skrbnika(status=status)

		# * ZABELEZI NOV VPIS ZA CLANA
		if status.clan.vpisan:
			status.napake.append(TipVpisnaNapaka.CLAN_JE_VPISAN)
			await self.poslji_porocilo_napake.exe(naslov="Db service napaka", opis="Clan nebi smel biti vpisan!", clan=status.clan)
		else:
			status.clan.nov_vpis()

		# * CE NI BILO NAPAK USTVARI PAYMENT CUSTOMERJA
		await self._create_payment_customer(
			status=status,
			billing_phone=vp.telefon_skrbnika if status.clan.mladoletnik else vp.telefon,
			billing_email=vp.email_skrbnika if status.clan.mladoletnik else vp.email)

		# * CE IMA UPORABNIK GITHUB GA POVABI V ORGANIZACIJO SAJ JE NJEGOV EMAIL ZE VALIDIRAN
		await self._vcs_vabilo_v_organizacijo(status=status, email=vp.email)

		# * SHRANI INFORMACIJE V BAZO
		self._shrani_v_bazo(status=status)

		# ! PO KONCANEM PREVERI DB CONSISTENCY!!!
		return status

	def _merge_clana_in_skrbnika(self, status: StatusVpisa):
		# * USTVARI CLANA IN GA POVEZI V BAZO!
		db_oseba: Oseba
		for db_oseba in self.db.find(entity=status.clan):
			status.informacije.append(TipVpisnaInformacija.CLAN_SE_PONOVNO_VPISUJE)
			db_oseba.merge(status.clan, merge_kontakti=True, merge_vpisi_izpisi=False)  # ? Vpis se zgodi po mergu, zato to ni treba mergat
			status.clan = db_oseba

		# * USTVARI SKRBNIKA IN GA POVEZI V BAZO!
		if status.clan.mladoletnik:
			status.informacije.append(TipVpisnaInformacija.CLAN_JE_MLADOLETNIK)
			for db_oseba in self.db.find(entity=status.skrbnik):
				status.informacije.append(TipVpisnaInformacija.SKRBNIK_SE_PONOVNO_VPISUJE)
				db_oseba.merge(status.skrbnik, merge_kontakti=True, merge_vpisi_izpisi=False)  # ? Vpis se zgodi po mergu, zato to ni treba mergat.
				status.skrbnik = db_oseba

	async def _create_payment_customer(self, status: StatusVpisa, billing_phone: str, billing_email: str):
		# * POISCI IZVOR BILLING TELEFONA
		izvor_telefona = self.phone.origin(phone=billing_phone)

		if len(izvor_telefona.languages) == 0:
			status.napake.append(TipVpisnaNapaka.IZVOR_TELEFONA_NI_NAJDEN)
			await self.poslji_porocilo_napake.exe(naslov="Phone service napaka", opis="Izvor telefona ni bil najden!", billing_phone=billing_phone)

		# * CE SE JE MERGE ZGODIL POTEM IMA ZE NASTAVLJEN ID OD STRIPE-a
		customer = self.payment.create_customer(customer=Customer(
			id=status.clan._id, name=f'{status.clan.ime} {status.clan.priimek}',
			billing_email=billing_email,
			languages=izvor_telefona.languages))

		# ! CE SE CUSTOMER NI USTVARIL NE NADALJUJ...
		if customer is None:
			status.napake.append(TipVpisnaNapaka.PAYMENT_CUSTOMER_FAIL)
			return await self.poslji_porocilo_napake.exe(
				naslov="Payment service napaka", opis="Payment customer se pri včlanitvi ni mogel ustvariti!",
				clan=status.clan, billing_phone=billing_phone, billing_email=billing_email)

		# * OBVEZNA POSODOBITEV ID KI SE UJEMA Z PAYMENT ID
		with self.db.transaction() as _:
			status.clan._id = customer.id

		# * PREVERI ZGODOVINO SUBSCRIPTIONS
		sub_history_status = customer.subscription_history_status(price=CONST.payment_prices.klubska_clanarina)
		trial_period_days = 0
		match sub_history_status:

			# * CE SE NI BIL NIKOLI NAROCEN
			case SubscriptionHistoryStatus.NEVER_SUBSCRIBED:
				status.informacije.append(TipVpisnaInformacija.POSKUSNO_OBDOBJE)
				trial_period_days = CONST.trial_period_days

			case SubscriptionHistoryStatus.IS_SUBSCRIBED:
				status.napake.append(TipVpisnaNapaka.PAYMENT_CUSTOMER_IS_SUBSCRIBED)
				return await self.poslji_porocilo_napake.exe(
					naslov="Payment service napaka", opis="Payment customer nebi smel biti naročen na naročnino!",
					clan=status.clan, billing_phone=billing_phone, billing_email=billing_email, customer=customer)

		# * CE NI ZE NAROCEN POTEM USTVARI SUBSCRIPTION NA KLUBSKO CLANARINO
		subscription = self.payment.create_subscription(subscription=Subscription(
			prices=[CONST.payment_prices.klubska_clanarina],
			customer=customer, collection_method=CollectionMethod.SEND_INVOICE,
			days_until_due=CONST.days_until_due, trial_period_days=trial_period_days))

		# ! CE SE SUBSCRIPTION NI MORALA USTVARITI POTEM KONCAJ...
		if subscription is None:
			status.napake.append(TipVpisnaNapaka.PAYMENT_SUBSCRIPTION_FAIL)
			return await self.poslji_porocilo_napake.exe(
				naslov="Payment service napaka", opis="Payment subcription se pri včlanitvi ni mogla ustvariti!",
				clan=status.clan, billing_phone=billing_phone, billing_email=billing_email, customer=customer)

		status.informacije.append(TipVpisnaInformacija.NAROCEN_NA_KLUBSKO_CLANARINO)

	def _shrani_v_bazo(self, status: StatusVpisa):
		with self.db.transaction(note=f'Shrani {status.clan}') as root:
			root.save(status.clan, unique=True)
			if status.clan.mladoletnik:
				status.clan.connect(status.skrbnik)
				root.save(status.skrbnik, unique=True)

	async def _vcs_vabilo_v_organizacijo(self, status: StatusVpisa, email: str):
		user = self.vcs.user(email=email)
		if user is None:
			return status.informacije.append(TipVpisnaInformacija.NIMA_VCS_PROFILA)

		if self.vcs.user_invite(email=email, member_role=VcsMemberRole.DIRECT_MEMBER):
			return status.informacije.append(TipVpisnaInformacija.POVABLJEN_V_VCS_ORGANIZACIJO)

		status.napake.append(TipVpisnaNapaka.VCS_INVITE_FAIL)
		return await self.poslji_porocilo_napake.exe(naslov="Vcs service napaka", opis="Vcs povabilo se pri včlanitvi ni moglo poslati!", email=email)
