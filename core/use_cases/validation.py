from dataclasses import dataclass

from core.domain.arhitektura_kluba import Kontakt, Clan
from core.services._utils import Validation
from core.services.email_service import EmailService
from core.services.sms_service import SmsService


@dataclass
class ClanUseCase:
	emailService: EmailService
	smsService: SmsService


class ValidateKontakt(ClanUseCase):
	def invoke(self, kontakt: Kontakt) -> list[Validation]:
		validations = []
		for fun, data in [
			(self.smsService.obstaja, kontakt.telefon),
			(self.emailService.obstaja, kontakt.email)]:
			validations.append(Validation(data, fun(data)))

		return validations


class ValidateClan(ClanUseCase):

	def invoke(self, clan: Clan) -> list[Validation]:
		validations = []
		for fun, data in [
			(self.smsService.obstaja, clan.telefon),
			(self.emailService.obstaja, clan.email)]:
			validations.append(Validation(data, fun(data)))

		return validations
