from dataclasses import dataclass
from typing import Any

from autologging import traced

from core.domain.arhitektura_kluba import Kontakt, TipKontakta
from core.domain.oznanila_sporocanja import Sporocilo
from core.services.db_service import DbService
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.use_cases._usecase import UseCase


@traced
@dataclass
class Poslji_sporocilo(UseCase):
	db: DbService
	phone: PhoneService
	email: EmailService

	async def exe(self, kontakt: Kontakt, naslov: str | None, vsebina: str) -> Any:
		sporocilo = Sporocilo(naslov=naslov, vsebina=vsebina)
		with self.db.transaction() as root:
			if kontakt.tip == TipKontakta.EMAIL:
				await self.email.send(recipients=[kontakt.data], subject=naslov, vsebina=vsebina)
			elif kontakt.tip == TipKontakta.PHONE:
				self.phone.send_sms(phone=kontakt.data, text=vsebina)
			kontakt.connect(sporocilo)
			root.save(sporocilo)
