import logging
import sys
from unittest.mock import MagicMock

import autologging
from autologging import traced
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, DependenciesContainer, Factory, Provider

from app import ENV, CONST
from app.db.db_zodb import DbZo
from app.services.auth_jwt import AuthJwt
from app.services.email_smtp import EmailSmtp
from app.services.payment_stripe import PaymentStripe
from app.services.phone_twilio import PhoneTwilio
from app.services.template_jinja import TemplateJinja
from core import cutils
from core.services.auth_service import AuthService
from core.services.db_service import DbService
from core.services.email_service import EmailService
from core.services.payment_service import PaymentService
from core.services.phone_service import PhoneService
from core.services.template_service import TemplateService
from core.use_cases.auth_cases import Auth_login, Auth_info, Auth_verification_token
from core.use_cases.db_cases import Db_path
from core.use_cases.forms_vpis import Forms_vpis
from core.use_cases.validation_cases import Validate_kontakt


class Services(DeclarativeContainer):
	auth: Provider[AuthJwt] = Singleton(AuthJwt, secret=ENV.SECRET_KEY)
	db: Provider[DbZo] = Singleton(DbZo, storage=ENV.DB_PATH)
	payment: Provider[PaymentStripe] = Singleton(PaymentStripe)
	phone: Provider[PhoneTwilio] = Singleton(
		PhoneTwilio, default_country_code=CONST.phone_country_code, from_number=ENV.TWILIO_FROM_NUMBER,
		service_sid=ENV.TWILIO_SERVICE_SID, account_sid=ENV.TWILIO_ACCOUNT_SID, auth_token=ENV.TWILIO_AUTH_TOKEN)
	email: Provider[EmailSmtp] = Singleton(
		EmailSmtp, name=CONST.klub, email=CONST.email,
		server=CONST.domain, port=ENV.MAIL_PORT,
		username=CONST.email, password=ENV.MAIL_PASSWORD,
		suppress_send=ENV.MAIL_SUPPRESS_SEND
	)
	template: Provider[TemplateJinja] = Singleton(TemplateJinja, searchpath=CONST.api_templates)


class TestServices(DeclarativeContainer):
	auth: Provider[AuthJwt] = Factory(MagicMock(set_spec=True, spec=AuthService))
	db: Provider[DbZo] = Factory(MagicMock(set_spec=True, spec=DbService))
	payment: Provider[PaymentStripe] = Factory(MagicMock(set_spec=True, spec=PaymentService))
	phone: Provider[PhoneTwilio] = Factory(MagicMock(set_spec=True, spec=PhoneService))
	email: Provider[EmailSmtp] = Factory(MagicMock(set_spec=True, spec=EmailService))
	template: Provider[TemplateJinja] = Factory(MagicMock(set_spec=True, spec=TemplateService))


class UseCases(DeclarativeContainer):
	d = DependenciesContainer()

	# OSEBA
	validate_kontakt: Provider[Validate_kontakt] = Factory(Validate_kontakt, email=d.email, phone=d.phone)

	# AUTH
	auth_login: Provider[Auth_login] = Factory(Auth_login, db=d.db, auth=d.auth)
	auth_info: Provider[Auth_info] = Factory(Auth_info, db=d.db, auth=d.auth)
	auth_verification_token: Provider[Auth_verification_token] = Factory(Auth_verification_token, db=d.db, auth=d.auth)

	# DB
	db_path: Provider[Db_path] = Factory(Db_path, db=d.db)
	forms_vpis: Provider = Factory(
		Forms_vpis, db=d.db, email=d.email, phone=d.phone, validate_kontakt=validate_kontakt, template=d.template,
		auth_verification_token=auth_verification_token)


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
	])


@traced
def init(seed: bool = False):
	if this.inited:
		log.info('APP already inited!!!')
		return

	this.services = Services()
	this.useCases = UseCases(d=services)
	this.db = this.services.db()

	this.db.open()
	if seed: this.db.seed()

	this.inited = True


__all__ = ['ENV', 'init', 'services', 'useCases']
