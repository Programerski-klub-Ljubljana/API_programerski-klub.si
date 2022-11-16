import logging
from dataclasses import dataclass

from autologging import traced

from core.domain.arhitektura_kluba import Kontakt, Clan
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
			(self.smsService.obstaja, kontakt.telefon),
			(self.emailService.obstaja, kontakt.email)]:
			validations.append(Validation(data, fun(data)))

		return validations


@traced
class Validate_clan(ClanUseCase):

	def invoke(self, clan: Clan) -> list[Validation]:
		validations = []
		for fun, data in [
			(self.smsService.obstaja, clan.telefon),
			(self.emailService.obstaja, clan.email)]:
			validations.append(Validation(data, fun(data)))

		return validations
