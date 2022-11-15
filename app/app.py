import sys
from typing import Callable

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, DependenciesContainer, Factory, Provider

from app import env
from app.db.zodb import ZoDB
from app.services.db_neoserv import NeoServ
from app.services.jwt_auth import JwtAuth
from app.services.payment_stripe import Stripe
from app.services.sms_twilio import Twilio
from core.services.auth_service import AuthService
from core.services.db_service import DbService
from core.services.email_service import EmailService
from core.services.payment_service import PaymentService
from core.services.sms_service import SmsService
from core.use_cases import validation
from core.use_cases.validation import ValidateKontakt, ValidateClan


class Services(DeclarativeContainer):
	auth: Provider[AuthService] = Singleton(JwtAuth)
	db: Provider[DbService] = Singleton(ZoDB)
	email: Provider[EmailService] = Singleton(NeoServ)
	payment: Provider[PaymentService] = Singleton(Stripe)
	sms: Provider[SmsService] = Singleton(Twilio, account_sid=env.TWILIO_ACCOUNT_SID, auth_token=env.TWILIO_AUTH_TOKEN)


class UseCases(DeclarativeContainer):
	dc = DependenciesContainer()

	# CLAN
	__deps = [dc.emailService, dc.smsService]
	validate_kontakt: Provider[ValidateKontakt] = Factory(validation.ValidateKontakt, *__deps)
	validate_clan: Provider[ValidateClan] = Factory(validation.ValidateClan, *__deps)


this = sys.modules[__name__]
services: Services
useCases: UseCases


def init(seed: bool):
	env.init()
	this.services = Services()
	this.useCases = UseCases(dc=this.services)

	if seed:
		this.services.db().seed()
