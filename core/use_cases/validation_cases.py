import logging
from dataclasses import dataclass

from autologging import traced

from core.domain.arhitektura_kluba import Kontakt
from core.services.email_service import EmailService
from core.services.sms_service import SmsService

log = logging.getLogger(__name__)


@dataclass
class Validation:
	data: str
	ok: bool


@dataclass
class ClanUseCase:
	emailService: EmailService
	smsService: SmsService


@traced
class Validate_kontakt(ClanUseCase):
	def invoke(self, kontakt: Kontakt) -> list[Validation]:
		validations = []
		for fun, data in [
			*((self.smsService.obstaja, tel) for tel in kontakt.telefon),
			*((self.emailService.obstaja, email) for email in kontakt.email)]:
			validations.append(Validation(data, fun(data)))

		return validations
