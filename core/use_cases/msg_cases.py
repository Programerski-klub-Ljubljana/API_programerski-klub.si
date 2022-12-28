from dataclasses import dataclass
from typing import Any

from autologging import traced

from app import CONST
from core.domain.arhitektura_kluba import Kontakt, TipKontakta, TipOsebe
from core.domain.oznanila_sporocanja import Sporocilo
from core.services.db_service import DbService
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.services.template_service import TemplateService
from core.use_cases._usecase import UseCase


@traced
@dataclass
class Poslji_sporocilo_kontaktu(UseCase):
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


@traced
@dataclass
class Poslji_porocilo_napake(UseCase):
	db: DbService
	phone: PhoneService
	email: EmailService
	template: TemplateService
	poslji_sporocilo_kontaktu: Poslji_sporocilo_kontaktu

	async def exe(self, naslov: str, opis: str, **kwargs) -> Any:
		temp = self.template.init(napaka=naslov, opis=opis, data=kwargs)
		with self.db.transaction() as root:
			for oseba in root.oseba:
				if TipOsebe.ADMIN == oseba.tip_osebe:
					for kontakt in oseba.kontakti:
						await self.poslji_sporocilo_kontaktu.exe(
							kontakt=kontakt,
							naslov=CONST.email_subject.porocilo_napake,
							vsebina=temp.porocilo_napake)
