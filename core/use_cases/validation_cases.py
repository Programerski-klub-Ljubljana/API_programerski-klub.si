import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from autologging import traced

from app import CONST
from core.domain.arhitektura_kluba import Kontakt, TipKontakta, NivoValidiranosti, Oseba
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.services.template_service import TemplateService, TemplateRenderer
from core.use_cases._usecase import UseCase
from core.use_cases.auth_cases import Ustvari_osebni_zeton
from core.use_cases.msg_cases import Poslji_sporocilo

log = logging.getLogger(__name__)


@dataclass
@traced
class Preveri_obstoj_kontakta(UseCase):
	email: EmailService
	phone: PhoneService

	def exe(self, *kontakti: Kontakt) -> list[Kontakt]:
		'''Vrne kontakte ki so bili validirani!'''

		mapping: dict[Enum, Callable] = {  # TODO: Make this global somehow...
			TipKontakta.EMAIL: self.email.check_existance,
			TipKontakta.PHONE: self.phone.check_existance
		}

		val_kontakti = []
		for kontakt in kontakti:
			val_fun = mapping[kontakt.tip]
			if kontakt.nivo_validiranosti == NivoValidiranosti.NI_VALIDIRAN:
				if val_fun(kontakt.data):
					kontakt.nivo_validiranosti = NivoValidiranosti.VALIDIRAN
				val_kontakti.append(kontakt)
		return val_kontakti


@traced
@dataclass
class Poslji_test_ki_preveri_lastnistvo_kontakta(UseCase):
	template: TemplateService
	msg_send: Poslji_sporocilo
	auth_verification_token: Ustvari_osebni_zeton

	async def exe(self, oseba: Oseba) -> list[Kontakt]:
		temp: TemplateRenderer = self.template.init(ime=oseba.ime, priimek=oseba.priimek)

		kontakti = []
		for kontakt in oseba.kontakti:
			if kontakt.nivo_validiranosti == NivoValidiranosti.VALIDIRAN:
				"""
					THIS SENDS KONTAKT _ID BECAUSE EMAILS WILL NOT BE UNIQUE AND CAN BE MULTIPLIED (CHILD, PARENTS)
				"""
				temp('token', self.auth_verification_token.exe(data=kontakt._id).data)
				kontakti.append(kontakt)
				if kontakt.tip == TipKontakta.EMAIL:
					await self.msg_send.exe(kontakt=kontakt, naslov=CONST.email_subject.verifikacija, vsebina=temp.email_verifikacija)
				elif kontakt.tip == TipKontakta.PHONE:
					await self.msg_send.exe(kontakt=kontakt, naslov=None, vsebina=temp.sms_verifikacija)

		return kontakti


@traced
@dataclass
class Poslji_test_ki_preveri_zeljo_za_koncno_izclanitev(UseCase):
	template: TemplateService
	msg_send: Poslji_sporocilo
	auth_verification_token: Ustvari_osebni_zeton

	async def exe(self, oseba: Oseba) -> Kontakt:
		temp: TemplateRenderer = self.template.init(ime=oseba.ime, priimek=oseba.priimek)

		"""
			THIS SENDS USER _ID BECAUSE EMAILS WILL NOT BE UNIQUE AND CAN BE MULTIPLIED (CHILD, PARENTS)
		"""
		temp('token', self.auth_verification_token.exe(data=oseba._id).data)

		for kontakt in oseba.kontakti:
			if kontakt.nivo_validiranosti == NivoValidiranosti.POTRJEN:
				if kontakt.tip == TipKontakta.EMAIL:
					await self.msg_send.exe(kontakt=kontakt, naslov=CONST.email_subject.verifikacija_izpisa, vsebina=temp.email_izpis_clan)
					return kontakt

		return None
