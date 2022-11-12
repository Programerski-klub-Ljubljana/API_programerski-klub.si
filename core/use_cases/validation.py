from dataclasses import dataclass

from core.domain.arhitektura_kluba import Kontakt, Clan
from core.services.email_service import EmailService
from core.services.sms_service import SmsService
from core.services.utils import Validation


@dataclass
class ClanUseCase:
	emailService: EmailService
	smsService: SmsService


class ValidateKontakt(ClanUseCase):
	def invoke(self, kontakt: Kontakt) -> list[Validation]:
		return [
			self.smsService.obstaja(kontakt.telefon),
			self.emailService.obstaja(kontakt.email)]


class ValidateClan(ClanUseCase):

	def invoke(self, clan: Clan) -> list[Validation]:
		return [
			self.smsService.obstaja(clan.telefon),
			self.emailService.obstaja(clan.email)]
