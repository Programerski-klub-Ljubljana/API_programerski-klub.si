import sys

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton, DependenciesContainer, Factory

from app import env
from app.services.neoserv import NeoServ
from app.services.jwt_auth import JwtAuth
from app.services.stripe import Stripe
from app.services.twilio import Twilio
from app.db.zodb import ZoDB
from core.use_cases import validation


class Adapters(DeclarativeContainer):
	auth = Singleton(JwtAuth)
	db = Singleton(ZoDB)
	email = Singleton(NeoServ)
	payment = Singleton(Stripe)
	sms = Singleton(Twilio, account_sid=env.TWILIO_ACCOUNT_SID, auth_token=env.TWILIO_AUTH_TOKEN)

class FakeAdapters(DeclarativeContainer):
	auth = Singleton(JwtAuth)
	db = Singleton(ZoDB)
	email = Singleton(NeoServ)
	payment = Singleton(Stripe)
	sms = Singleton(Twilio, account_sid=env.TWILIO_ACCOUNT_SID, auth_token=env.TWILIO_AUTH_TOKEN)

class UseCases(DeclarativeContainer):
	dc = DependenciesContainer()

	# CLAN
	__deps = [dc.emailService, dc.smsService]
	validate_kontakt = Factory(validation.ValidateKontakt, *__deps)
	validate_clan = Factory(validation.ValidateClan, *__deps)


this = sys.modules[__name__]
adapters: Adapters
useCases: UseCases


def init():
	env.init()
	this.adapters = Adapters()
	this.useCases = UseCases(dc=this.adapters)
