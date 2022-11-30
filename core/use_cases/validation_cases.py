import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from autologging import traced

from app import CONST
from core.domain.arhitektura_kluba import Kontakt, TipKontakta, TipValidacije, Oseba
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.services.template_service import TemplateService, TemplateRenderer
from core.use_cases._usecase import UseCase
from core.use_cases.auth_cases import Auth_verification_token
from core.use_cases.msg_cases import Msg_send

log = logging.getLogger(__name__)


@dataclass
@traced
class Validate_kontakts_existances(UseCase):
	email: EmailService
	phone: PhoneService

	def invoke(self, *kontakti: Kontakt) -> list[Kontakt]:
		'''Vrne kontakte ki so bili validirani!'''

		mapping: dict[Enum, Callable] = {  # TODO: Make this global somehow...
			TipKontakta.EMAIL: self.email.obstaja,
			TipKontakta.PHONE: self.phone.obstaja
		}

		val_kontakti = []
		for kontakt in kontakti:
			val_fun = mapping[kontakt.tip]
			if kontakt.validacija == TipValidacije.NI_VALIDIRAN:
				if val_fun(kontakt.data):
					kontakt.validacija = TipValidacije.VALIDIRAN
				val_kontakti.append(kontakt)
		return val_kontakti


@traced
@dataclass
class Validate_kontakts_ownerships(UseCase):
	template: TemplateService
	msg_send: Msg_send
	auth_verification_token: Auth_verification_token

	async def invoke(self, oseba: Oseba):
		temp: TemplateRenderer = self.template.init(ime=oseba.ime, priimek=oseba.priimek)

		for kontakt in oseba.kontakti:
			if kontakt.validacija == TipValidacije.VALIDIRAN:
				temp('token', self.auth_verification_token.invoke(kontakt.data).data)
				if kontakt.tip == TipKontakta.EMAIL:
					await self.msg_send.invoke(kontakt=kontakt, naslov=CONST.email_subject.verifikacija, vsebina=temp.email_verifikacija)
				elif kontakt.tip == TipKontakta.PHONE:
					await self.msg_send.invoke(kontakt=kontakt, naslov=None, vsebina=temp.sms_verifikacija)
