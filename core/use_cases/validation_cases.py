import logging
from dataclasses import dataclass

from autologging import traced

from core.domain.arhitektura_kluba import Kontakt
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService

log = logging.getLogger(__name__)


@dataclass
class Validation:
	title: str
	data: str
	ok: bool

	def __str__(self):
		test = "OK" if self.ok else "ERR"
		return f'[{test}] {self.data}: {self.title}'

@dataclass
class ClanUseCase:
	emailService: EmailService
	smsService: PhoneService


@traced
class Validate_kontakt(ClanUseCase):
	def invoke(self, kontakt: Kontakt) -> list[Validation]:
		validacija = [(self.smsService.obstaja, tel, f'{kontakt.ime} {kontakt.priimek} (telefon)') for tel in kontakt.telefon]
		validacija += [(self.emailService.obstaja, email, f'{kontakt.ime} {kontakt.priimek} (email)') for email in kontakt.email]

		results = []
		for fun, data, title in validacija:
			results.append(Validation(ok=fun(data), data=data, title=title))

		return results
