import json
import unittest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, AsyncMock

from app import APP, CONST
from core.domain.arhitektura_kluba import TipKontakta, NivoValidiranosti, TipOsebe, Kontakt, Oseba
from core.services.auth_service import TokenData
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.services.vcs_service import VcsService
from core.use_cases.auth_cases import TokenPart
from core.use_cases.zacni_vclanitveni_postopek import StatusVpisa, Pripravi_vclanitveni_postopek, VpisniPodatki, ERROR_CLAN_JE_CHUCK_NORIS, \
	ERROR_CLAN_JE_ZE_VPISAN, ERROR_VALIDACIJA_KONTAKTOV, \
	ERROR_NEVELJAVEN_TOKEN, ERROR_VPISNI_PODATKI_DECODE


def vpisni_podatki(clan: Oseba, skrbnik: Oseba):
	vp = VpisniPodatki(
		ime=clan.ime,
		priimek=clan.priimek,
		dan_rojstva=clan.rojen.day,
		mesec_rojstva=clan.rojen.month,
		leto_rojstva=clan.rojen.year,
		email=clan.kontakti[0].data,
		telefon=clan.kontakti[1].data)

	if skrbnik is not None:
		vp.ime_skrbnika = skrbnik.ime
		vp.priimek_skrbnika = skrbnik.priimek
		vp.email_skrbnika = skrbnik.kontakti[0].data
		vp.telefon_skrbnika = skrbnik.kontakti[1].data
	return vp


class Test_VpisniPodatki(unittest.TestCase):
	skrbnik = None
	clan = None

	@classmethod
	def setUpClass(cls) -> None:
		cls.clan = Oseba(
			ime='clan.ime', priimek='clan.priimek',
			tip_osebe=[TipOsebe.CLAN], rojen=date(year=1234, month=2, day=1),
			kontakti=[
				Kontakt(data='email', tip=TipKontakta.EMAIL),
				Kontakt(data='telefon', tip=TipKontakta.PHONE)])

		cls.skrbnik = Oseba(
			ime='skrbnik.ime', priimek='skrbnik.priimek',
			tip_osebe=[TipOsebe.SKRBNIK], rojen=None,
			kontakti=[
				Kontakt(data='skrbnik.email', tip=TipKontakta.EMAIL),
				Kontakt(data='skrbnik.telefon', tip=TipKontakta.PHONE)])

		cls.vp = vpisni_podatki(clan=cls.clan, skrbnik=cls.skrbnik)

	def test_clan_skrbnik(self):
		ni_val_clan = self.vp.clan(nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)
		pot_clan = self.vp.clan(nivo_validiranosti=NivoValidiranosti.POTRJEN)

		ni_val_skrbnik = self.vp.skrbnik(nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN)
		pot_skrbnik = self.vp.skrbnik(nivo_validiranosti=NivoValidiranosti.POTRJEN)

		for clan, nivo in [(ni_val_clan, NivoValidiranosti.NI_VALIDIRAN), (pot_clan, NivoValidiranosti.POTRJEN)]:
			for k in self.clan.kontakti:
				k.nivo_validiranosti = nivo
			self.assertEqual(clan, self.clan)

		for skrbnik, nivo in [(ni_val_skrbnik, NivoValidiranosti.NI_VALIDIRAN), (pot_skrbnik, NivoValidiranosti.POTRJEN)]:
			for k in self.skrbnik.kontakti:
				k.nivo_validiranosti = nivo
			self.assertEqual(skrbnik, self.skrbnik)

	def test_encode_decode_clan_skrbnik(self):
		encoded = self.vp.encode()
		print(encoded)
		self.assertIsInstance(encoded, str)
		self.assertEqual(self.vp, VpisniPodatki.decode(encoded))

	def test_encode_decode_clan(self):
		for k, v in self.vp.__dict__.items():
			if k.endswith('_skrbnika'):
				setattr(self.vp, k, None)
		encoded = self.vp.encode()
		self.assertIsInstance(encoded, str)
		self.assertEqual(self.vp, VpisniPodatki.decode(encoded))

	def test_error_decode(self):
		self.assertIsNone(VpisniPodatki.decode('{{}}}'))


class Test_pripravi_vclanitveni_postopek(unittest.IsolatedAsyncioTestCase):
	case = None
	phone_service = None
	validate_kontakts_ownerships = None
	validate_kontakts_existances = None

	def setUp(self) -> None:
		APP.init(seed=False)
		self._init()

	def _init(self):
		# MOCKS
		self.phone_service: PhoneService = MagicMock(PhoneService, name='PhoneService')
		self.email_service: EmailService = MagicMock(EmailService, name='EmailService')

		# MOCKS LOGIC
		self.phone_service.format.side_effect = APP.services.phone().format
		self.phone_service.check_existance.side_effect = lambda phone: phone != 'xxx' and phone is not None
		self.email_service.check_existance.side_effect = lambda email: email != 'xxx' and email is not None

		# SETUP
		self.case: Pripravi_vclanitveni_postopek = APP.cases.pripravi_vclanitveni_postopek(
			phone=self.phone_service, email=self.email_service)

		self.case.send_token_parts.email.send = AsyncMock()
		self.case.send_token_parts.phone.send_sms = MagicMock()

		# VARIABLES
		self.today = date.today()

		self.skrbnik = Oseba(ime='ime_skrbnika', priimek='priimek_skrbnika', rojen=None, kontakti=[
			Kontakt(data=CONST.emails.test2, tip=TipKontakta.EMAIL), Kontakt(data=CONST.phones.test2, tip=TipKontakta.PHONE)])

		self.polnoletna_oseba = Oseba(ime='ime', priimek='priimek', rojen=date(year=self.today.year - 20, month=1, day=1), kontakti=[
			Kontakt(data=CONST.emails.test_vcs_member, tip=TipKontakta.EMAIL), Kontakt(data=CONST.phones.test, tip=TipKontakta.PHONE)])

		self.mladoletna_oseba = Oseba(ime='ime', priimek='priimek', rojen=date(year=self.today.year - 10, month=1, day=1), kontakti=[
			Kontakt(data=CONST.emails.test_vcs_member, tip=TipKontakta.EMAIL), Kontakt(data=CONST.phones.test, tip=TipKontakta.PHONE)])

		self.vp = None

		# CLEAN DB
		with self.case.db.transaction() as root:
			root.oseba.clear()
			assert len(root.oseba) == 0

	async def _exe(self, clan: Oseba, skrbnik: Oseba = None):
		token_parts = await self.case.exe(vp=vpisni_podatki(clan=clan, skrbnik=skrbnik))

		# * PREVERI ALI TOKEN PARTS DOBI ZACETNO STANJE
		token = TokenPart.merge(token_parts)
		body = json.loads(self.case.auth.decode(token).d)
		vp = VpisniPodatki(*body)
		self.assertEqual(vp, self.vp)

		# * PREVERI ALI JE TELEFON FORMATIRAN
		self.assertTrue(vp.telefon.startswith('+'), vp.telefon)
		if clan.mladoletnik:
			self.assertTrue(vp.telefon_skrbnika.startswith('+'), vp.telefon_skrbnika)

		return token

	async def test_error_clan_je_chuck_noris(self):
		with self.assertRaises(ERROR_CLAN_JE_CHUCK_NORIS):
			await self._exe(clan=self.mladoletna_oseba, skrbnik=self.mladoletna_oseba)

		with self.assertRaises(ERROR_CLAN_JE_CHUCK_NORIS):
			await self._exe(clan=self.polnoletna_oseba, skrbnik=self.polnoletna_oseba)

	async def test_error_clan_je_ze_vpisan(self):
		with self.case.db.transaction() as root:
			self.mladoletna_oseba.nov_vpis()
			root.save(self.mladoletna_oseba)

			self.polnoletna_oseba.nov_vpis()
			root.save(self.polnoletna_oseba)

		with self.assertRaises(ERROR_CLAN_JE_ZE_VPISAN):
			await self._exe(clan=self.mladoletna_oseba, skrbnik=self.skrbnik)

		with self.assertRaises(ERROR_CLAN_JE_ZE_VPISAN):
			await self._exe(clan=self.polnoletna_oseba)

	async def test_error_validacija_kontaktov(self):
		# MLADOLETNIK
		self.mladoletna_oseba.kontakti[0].data = 'xxx'
		with self.assertRaises(ERROR_VALIDACIJA_KONTAKTOV):
			await self._exe(clan=self.mladoletna_oseba, skrbnik=self.skrbnik)

		self._init()

		self.mladoletna_oseba.kontakti[1].data = 'xxx'
		with self.assertRaises(ERROR_VALIDACIJA_KONTAKTOV):
			await self._exe(clan=self.mladoletna_oseba, skrbnik=self.skrbnik)

		self._init()

		# SKRBNIK MLADOLETNIKA
		self.skrbnik.kontakti[0].data = 'xxx'
		with self.assertRaises(ERROR_VALIDACIJA_KONTAKTOV):
			await self._exe(clan=self.mladoletna_oseba, skrbnik=self.skrbnik)

		self._init()

		self.skrbnik.kontakti[1].data = 'xxx'
		with self.assertRaises(ERROR_VALIDACIJA_KONTAKTOV):
			await self._exe(clan=self.mladoletna_oseba, skrbnik=self.skrbnik)

		self._init()

		# POLNOLETNIK
		self.polnoletna_oseba.kontakti[0].data = 'xxx'
		with self.assertRaises(ERROR_VALIDACIJA_KONTAKTOV):
			await self._exe(clan=self.polnoletna_oseba)

		self._init()

		self.polnoletna_oseba.kontakti[1].data = 'xxx'
		with self.assertRaises(ERROR_VALIDACIJA_KONTAKTOV):
			await self._exe(clan=self.polnoletna_oseba)

	async def test_mladoletnik(self):
		await self._exe(clan=self.mladoletna_oseba, skrbnik=self.skrbnik)

	async def test_polnoletnik(self):
		await self._exe(clan=self.polnoletna_oseba)


class Test_zacni_vclanitveni_postopek(unittest.IsolatedAsyncioTestCase):
	case = None
	phone_service = None
	validate_kontakts_ownerships = None
	validate_kontakts_existances = None

	def setUp(self) -> None:
		APP.init(seed=False)

		# MOCKS
		self.phone_service: PhoneService = MagicMock(PhoneService, name='PhoneService')
		self.vcs_service: VcsService = MagicMock(VcsService, name='VcsService')

		# SETUP
		self.case = APP.cases.zacni_vclanitveni_postopek(
			phone=self.phone_service,
			vcs=self.vcs_service)

		self.today = date.today()
		self.skrbnik = Oseba(ime='ime_skrbnika', priimek='priimek_skrbnika', rojen=None, kontakti=[
			Kontakt(data=CONST.emails.test2, tip=TipKontakta.EMAIL), Kontakt(data='041327791', tip=TipKontakta.PHONE)])
		self.polnoletna_oseba = Oseba(ime='ime', priimek='priimek', rojen=date(year=self.today.year - 20, month=1, day=1), kontakti=[
			Kontakt(data=CONST.emails.test_vcs_member, tip=TipKontakta.EMAIL), Kontakt(data=CONST.phones.test, tip=TipKontakta.PHONE)])
		self.mladoletna_oseba = Oseba(ime='ime', priimek='priimek', rojen=date(year=self.today.year - 10, month=1, day=1), kontakti=[
			Kontakt(data=CONST.emails.test_vcs_member, tip=TipKontakta.EMAIL), Kontakt(data=CONST.phones.test, tip=TipKontakta.PHONE)])

		# * CLEAN DATABASE
		with self.case.db.transaction() as root:
			root.oseba.clear()
			assert len(root.oseba) == 0

	def _assertEqualProperties(self, status: StatusVpisa, expected):
		prop = []
		for k, v in status.__dict__.items():
			if isinstance(v, list) and len(v) > 0:
				prop.append(k)
			elif isinstance(v, Oseba | MagicMock) and v is not None:
				prop.append(k)

		self.assertCountEqual(sorted(prop), sorted(expected))

	def _assertEqualOseba(self, original_oseba, status_oseba, vpis: bool = False, tip: TipOsebe = TipOsebe.CLAN):
		# * MORA IMETI ENAKE INFORMACIJE
		self.assertEqual(original_oseba.ime, status_oseba.ime)
		self.assertEqual(original_oseba.priimek, status_oseba.priimek)
		self.assertEqual(original_oseba.rojen, status_oseba.rojen)

		# * ENAKO STEVILO KONTAKTOV
		self.assertEqual(len(original_oseba.kontakti), len(status_oseba.kontakti))
		for i, k1 in enumerate(original_oseba.kontakti):
			k2 = status_oseba.kontakti[i]
			self.assertEqual(k1.tip, k2.tip)
			self.assertEqual(k1.data, k2.data)

		# * MORA BITI VPISAN
		# ! self.assertEqual(vpis, status_oseba.vpisan)

		# * MORA BITI PRAVEGA TIPA
		# ! self.assertIn(tip, status_oseba.tip_osebe)

	async def _exe(self, clan: Oseba, skrbnik: Oseba = None, db_saved: bool = True, existing: bool = False):

		# * PRIRAVI ZA KLIC
		vp = vpisni_podatki(clan=clan, skrbnik=skrbnik)
		token = self.case.auth.encode(token_data=TokenData(data=vp.encode()), expiration=CONST.auth_verification_token_life)

		# * INVOKE
		before = datetime.now() - timedelta(seconds=1)
		status: StatusVpisa = await self.case.exe(token=token.data)
		after = datetime.now() + timedelta(seconds=1)

		# * PREVERI ALI JE CLAN V VPISNEM STATUSU
		# * PREVERI CE SO PROPERTIJI CLANA VSI COOL
		self._assertEqualOseba(original_oseba=clan, status_oseba=status.clan, vpis=db_saved, tip=TipOsebe.CLAN)
		if skrbnik is not None:
			self._assertEqualOseba(original_oseba=skrbnik, status_oseba=status.skrbnik, vpis=False, tip=TipOsebe.SKRBNIK)

		# TODO: PREVERI ALI SE JE MERGE ZGODIL...
		# * PREVERI CE SO SE STVARI PRAVILNO SHRANILE IN POVEZALE MED SABO V DB-ju
		with self.case.db.transaction() as root:
			if db_saved:
				self.assertEqual(len(root.oseba), 1 if skrbnik is None else 2)
				self.assertEqual(root.oseba[0], status.clan)
				if skrbnik is not None:
					self.assertEqual(root.oseba[1], status.skrbnik)
					self.assertEqual(root.oseba[0]._connections, [status.skrbnik])
					self.assertEqual(root.oseba[1]._connections, [status.clan])
			# !  else:
				# ! self.assertEqual(len(root.oseba), 0)

		# * PREVERI ALI SE JE CUSTOMER V PAYMENT DODAL IN AKTIVIRAL SUBSCRIPTION NA NJEMU.
		customer = self.case.payment.get_customer(id=status.clan._id)
		if db_saved:
			c = status.clan
			s = status.skrbnik
			self.assertTrue(customer.id.startswith('cus_'))
			self.assertEqual(customer.id, c._id)
			self.assertEqual(customer.name, f'{c.ime} {c.priimek}')
			self.assertEqual(customer.billing_email, [k.data for k in (s.kontakti if c.mladoletnik else c.kontakti) if k.tip == TipKontakta.EMAIL][0])
			self.assertEqual(customer.description, None)
			self.assertEqual(customer.balance, 0)
			self.assertEqual(customer.discount, None)
			self.assertEqual(customer.delinquent, False)
			self.assertEqual(customer.languages, ['sl'])
			self.assertEqual(customer.deleted, False)
			if not existing:
				self.assertTrue(before < customer.created < after, f'{before} {customer.created} {after}')
			else:
				self.assertTrue(customer.created < after, f'{customer.created} {after}')
		else:
			self.assertIsNone(customer, msg=customer)

		# * PREVERI ALI SE JE VABILO V VCS POSLALO

		return status

	async def test_error_neveljaven_token(self):
		with self.assertRaises(ERROR_NEVELJAVEN_TOKEN):
			await self.case.exe(token='xxx')

	async def test_error_vpisni_podatki_decode(self):
		with self.assertRaises(ERROR_VPISNI_PODATKI_DECODE):
			await self.case.exe(token=self.case.auth.encode(token_data=TokenData(data='xxx'), expiration=CONST.auth_verification_token_life).data)

	async def test_nov_polnoletni_clan(self):
		status = await self._exe(clan=self.polnoletna_oseba, db_saved=False)
		self._assertEqualProperties(status, ['clan', 'skrbnik', 'napake', 'informacije'])
		self.assertEqual(status.napake, [])
		self.assertEqual(status.informacije, [])


if __name__ == '__main__':
	unittest.main()
