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

		validacija = [(self.smsService.obstaja, tel) for tel in kontakt.telefon]
		validacija += [(self.emailService.obstaja, email) for email in kontakt.email]

		results = []
		for fun, data in validacija:
			results.append(Validation(data, fun(data)))

		return results
