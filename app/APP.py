import logging
import sys

from autologging import traced
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, DependenciesContainer, Factory, Provider

from app import ENV, CONST
from app.db.db_zodb import DbZo
from app.services.auth_jwt import AuthJwt
from app.services.email_smtp import Email_smtp_imap
from app.services.github_vcs import GithubVcs
from app.services.payment_stripe import PaymentStripe
from app.services.phone_twilio import PhoneTwilio
from app.services.template_jinja import TemplateJinja
from core import cutils
from core.services.db_service import DbService
from core.use_cases.auth_cases import Vpisi_osebo, Vpisne_informacije, Ustvari_osebni_zeton, Vclani_osebo, Izpisi_osebo
from core.use_cases.db_cases import Vrni_vsebino_baze
from core.use_cases.msg_cases import Poslji_sporocilo
from core.use_cases.validation_cases import Preveri_obstoj_kontakta, Poslji_test_ki_preveri_lastnistvo_kontakta, \
	Poslji_test_ki_preveri_zeljo_za_koncno_izclanitev
from core.use_cases.zacni_izclanitveni_postopek import Zacni_izclanitveni_postopek
from core.use_cases.zacni_vclanitveni_postopek import Zacni_vclanitveni_postopek


class Services(DeclarativeContainer):
	auth: Provider[AuthJwt] = Singleton(AuthJwt, secret=ENV.SECRET_KEY)
	db: Provider[DbZo] = Singleton(DbZo, storage=ENV.DB_PATH, default_password=ENV.DB_DEFAULT_PASSWORD)
	payment: Provider[PaymentStripe] = Singleton(PaymentStripe, api_key=ENV.STRIPE_API_KEY)
	vcs: Provider[GithubVcs] = Singleton(
		GithubVcs, app_id=ENV.GITHUB_APP_ID, private_key_path=ENV.GITHUB_PRIVATE_KEY_PATH, organization=CONST.github_org)
	phone: Provider[PhoneTwilio] = Singleton(
		PhoneTwilio, default_country_code=CONST.phone_default_country_code, from_number=CONST.phones.api,
		service_sid=ENV.TWILIO_SERVICE_SID, account_sid=ENV.TWILIO_ACCOUNT_SID, auth_token=ENV.TWILIO_AUTH_TOKEN)
	email: Provider[Email_smtp_imap] = Singleton(
		Email_smtp_imap, name=CONST.org_name, email=CONST.emails.api,
		server=CONST.domain, port=ENV.MAIL_PORT,
		username=CONST.emails.api, password=ENV.MAIL_PASSWORD,
		suppress_send=ENV.MAIL_SUPPRESS_SEND
	)
	template: Provider[TemplateJinja] = Singleton(TemplateJinja, searchpath=CONST.api_templates)


class UseCases(DeclarativeContainer):
	d: Services = DependenciesContainer()

	""" FIRST LEVEL USE CASES """

	poslji_sporocilo: Provider[Poslji_sporocilo] = Factory(Poslji_sporocilo, db=d.db, phone=d.phone, email=d.email)

	# AUTH
	vpisi_osebo: Provider[Vpisi_osebo] = Factory(Vpisi_osebo, db=d.db, auth=d.auth)
	preberi_informacije_osebnega_zetona: Provider[Vpisne_informacije] = Factory(Vpisne_informacije, db=d.db, auth=d.auth)
	ustvari_osebni_zeton: Provider[Ustvari_osebni_zeton] = Factory(Ustvari_osebni_zeton, db=d.db, auth=d.auth)
	vclani_osebo: Provider[Vclani_osebo] = Factory(Vclani_osebo, db=d.db, auth=d.auth)
	izpisi_osebo: Provider[Izpisi_osebo] = Factory(Izpisi_osebo, db=d.db, auth=d.auth)

	# DB
	vrni_vsebino_baze: Provider[Vrni_vsebino_baze] = Factory(Vrni_vsebino_baze, db=d.db)

	# OSEBA
	preveri_obstoj_kontakta: Provider[Preveri_obstoj_kontakta] = Factory(Preveri_obstoj_kontakta, email=d.email, vcs=d.vcs, phone=d.phone)
	poslji_test_ki_preveri_lastnistvo_kontakta: Provider[Poslji_test_ki_preveri_lastnistvo_kontakta] = Factory(
		Poslji_test_ki_preveri_lastnistvo_kontakta, template=d.template, msg_send=poslji_sporocilo, auth_verification_token=ustvari_osebni_zeton)
	poslji_test_ki_preveri_zeljo_za_koncno_izclanitev: Provider[Poslji_test_ki_preveri_zeljo_za_koncno_izclanitev] = Factory(
		Poslji_test_ki_preveri_zeljo_za_koncno_izclanitev, template=d.template, msg_send=poslji_sporocilo,
		auth_verification_token=ustvari_osebni_zeton)

	# FORMS
	zacni_vclanitveni_postopek: Provider[Zacni_vclanitveni_postopek] = Factory(
		Zacni_vclanitveni_postopek, db=d.db, phone=d.phone, payment=d.payment, vcs=d.vcs,
		validate_kontakts_existances=preveri_obstoj_kontakta,
		validate_kontakts_ownerships=d.validate_kontakts_ownerships)
	zacni_izclanitveni_postopek: Provider[Zacni_izclanitveni_postopek] = Factory(
		Zacni_izclanitveni_postopek, db=d.db, validate_izpis_request=poslji_test_ki_preveri_zeljo_za_koncno_izclanitev)


log = logging.getLogger(__name__)

this = sys.modules[__name__]
inited: bool = False
db: DbService
services: Services
cases: UseCases

logging.basicConfig(
	level=ENV.LOG_LEVEL,
	format="%(filename)+20s ┃ %(funcName)-30s ┃ %(levelname)+8s ┃ %(message)s",
	handlers=[
		logging.FileHandler(cutils.root_path("logging.log"), mode='w'),
		logging.StreamHandler()
	])


@traced
def init(seed: bool = False):
	if this.inited:
		log.info('APP already inited!!!')
		return

	this.services = Services()
	this.cases = UseCases(d=services)
	this.db = this.services.db()

	this.db.open()
	if seed: this.db.seed()

	this.inited = True


__all__ = ['ENV', 'init', 'services', 'cases']
