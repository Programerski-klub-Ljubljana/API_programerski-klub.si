import logging
import sys

import autologging
from autologging import traced
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, DependenciesContainer, Factory, Provider

from app import ENV, CONST
from app.db.db_zodb import ZoDB
from app.services.auth_jwt import JwtAuth
from app.services.email_smtp import SmtpEmail
from app.services.payment_stripe import Stripe
from app.services.phone_twilio import Twilio
from core import cutils
from core.services.auth_service import AuthService
from core.services.db_service import DbService
from core.services.email_service import EmailService
from core.services.payment_service import PaymentService
from core.services.phone_service import PhoneService
from core.use_cases import validation_cases, db_cases, auth_cases


class Services(DeclarativeContainer):
	auth: Provider[AuthService] = Singleton(JwtAuth, secret=ENV.SECRET_KEY)
	db: Provider[DbService] = Singleton(ZoDB, storage=ENV.DB_PATH)
	payment: Provider[PaymentService] = Singleton(Stripe)
	phone: Provider[PhoneService] = Singleton(
		Twilio, default_country_code=CONST.phone_country_code,
		account_sid=ENV.TWILIO_ACCOUNT_SID, auth_token=ENV.TWILIO_AUTH_TOKEN)
	email: Provider[EmailService] = Singleton(
		SmtpEmail, name=CONST.klub, email=CONST.email,
		server=CONST.domain, port=ENV.MAIL_PORT,
		username=CONST.email, password=ENV.MAIL_PASSWORD)


class UseCases(DeclarativeContainer):
	dc = DependenciesContainer()

	# CLAN
	__deps = [dc.email, dc.phone]
	validate_kontakt = Factory(validation_cases.Validate_kontakt, *__deps)

	# AUTH
	__deps = [dc.auth, dc.db]
	auth_login = Factory(auth_cases.Auth_login, *__deps)
	auth_info = Factory(auth_cases.Auth_info, *__deps)

	# DB
	__deps = [dc.db]
	db_path = Factory(db_cases.Db_path, *__deps)


log = logging.getLogger(__name__)

this = sys.modules[__name__]
inited: bool = False
db: DbService
services: Services
useCases: UseCases

logging.basicConfig(
	level=logging.INFO if False else autologging.TRACE,
	format="%(filename)+20s ┃ %(funcName)-30s ┃ %(levelname)+8s ┃ %(message)s",
	handlers=[
		logging.FileHandler(cutils.root_path("logging.log"), mode='w'),
		logging.StreamHandler()
	]
)


@traced
def init(seed: bool = False):
	if this.inited:
		log.info('APP already inited!!!')
		return

	this.services = Services()
	this.useCases = UseCases(dc=services)
	this.db = this.services.db()

	this.db.open()
	if seed: this.db.seed()

	this.inited = True


__all__ = ['ENV', 'init', 'services', 'useCases']
