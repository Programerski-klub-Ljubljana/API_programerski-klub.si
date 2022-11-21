import logging
from dataclasses import dataclass

from autologging import traced

from core.domain.arhitektura_kluba import Kontakt, TipKontakta, TipValidacije
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.use_cases._usecase import UseCase

log = logging.getLogger(__name__)


@traced
@dataclass
class Validate_kontakt(UseCase):
	email: EmailService
	phone: PhoneService

	def invoke(self, *kontakti: Kontakt) -> list[Kontakt]:
		'''Vrne kontakte ki so bili validirani!'''

		mapping = {
			TipKontakta.EMAIL: self.email.obstaja,
			TipKontakta.PHONE: self.phone.obstaja
		}

		val_kontakti = []
		for kontakt in kontakti:
			val_fun = mapping[kontakt.tip]
			if kontakt.validacija == TipValidacije.NI_VALIDIRAN:
				kontakt.validacija = val_fun(kontakt.data)
				val_kontakti.append(kontakt)
		return val_kontakti
