import logging
import sys

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, DependenciesContainer, Factory, Provider

from app import ENV
from app.db.db_zodb import ZoDB
from app.services.email_neoserv import NeoServ
from app.services.jwt_auth import JwtAuth
from app.services.payment_stripe import Stripe
from app.services.sms_twilio import Twilio
from core.services.auth_service import AuthService
from core.services.db_service import DbService
from core.services.email_service import EmailService
from core.services.payment_service import PaymentService
from core.services.sms_service import SmsService
from core.use_cases import validation_cases, db_cases, auth_cases

log = logging.getLogger(__name__)

logging.basicConfig(
	level=logging.INFO,
	format="%(levelname)s | %(message)s",
	handlers=[
		logging.FileHandler("log_file.log"),
		logging.StreamHandler()
	]
)


class Services(DeclarativeContainer):
	auth: Provider[AuthService] = Singleton(JwtAuth)
	db: Provider[DbService] = Singleton(ZoDB, storage=ENV.DB_PATH)
	email: Provider[EmailService] = Singleton(NeoServ)
	payment: Provider[PaymentService] = Singleton(Stripe)
	sms: Provider[SmsService] = Singleton(Twilio, account_sid=ENV.TWILIO_ACCOUNT_SID, auth_token=ENV.TWILIO_AUTH_TOKEN)


class UseCases(DeclarativeContainer):
	dc = DependenciesContainer()

	# CLAN
	__deps = [dc.email, dc.sms]
	validate_kontakt = Factory(validation_cases.Validate_kontakt, *__deps)
	validate_clan = Factory(validation_cases.Validate_clan, *__deps)

	# AUTH
	__deps = [dc.auth, dc.db]
	auth_login = Factory(auth_cases.Auth_login, *__deps)

	# DB
	__deps = [dc.db]
	db_path = Factory(db_cases.Db_path, *__deps)


this = sys.modules[__name__]
inited: bool = False
db: DbService
services: Services
useCases: UseCases


def init(seed: bool = False):
	if this.inited:
		print('APP already inited!!!')
		return

	log.info("loguru info log")

	ENV.init()

	this.services = Services()
	this.useCases = UseCases(dc=services)
	this.db = this.services.db()

	this.db.open()
	if seed: this.db.seed()

	this.inited = True


__all__ = ['ENV', 'init', 'services', 'useCases']
