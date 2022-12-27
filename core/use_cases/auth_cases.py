from dataclasses import dataclass

from app import CONST
from core.domain.arhitektura_kluba import Kontakt, TipKontakta
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.services.template_service import TemplateService, TemplateRenderer
from core.use_cases._usecase import UseCase


@dataclass
class TokenPart:
	order: int
	data: str
	info: str = None

	@staticmethod
	def merge(parts: list['TokenPart']) -> str:
		token = ''
		for part in sorted(parts, key=lambda p: p.order, reverse=True):
			token += part.data
		return token


@dataclass
class Send_token_parts(UseCase):
	phone: PhoneService
	email: EmailService
	template: TemplateService

	async def exe(self, token: str, kontakti: list[Kontakt]) -> list[TokenPart]:
		token_parts = []

		# * PREVERI OVNERSHIP ZA KONTAKTE
		temp: TemplateRenderer = self.template.init()
		i = 0
		for kontakt in kontakti:
			# * CALCULATE NEXT TOKEN PART
			limit = len(token) - CONST.auth_verification_size
			token: str = token[:limit]
			token_part: str = token[limit:]

			# * TOKEN PARTS FROM 0...n
			tp = TokenPart(order=i, info=kontakt.data, data=token_part)
			i += 1
			token_parts.append(tp)

			# * SEND TOKEN MESSAGE
			temp.set(token=token_part)
			match kontakt.tip:
				case TipKontakta.EMAIL:
					await self.email.send(recipients=[kontakt.data], subject=CONST.email_subject.verifikacija, vsebina=temp.email_verifikacija)
				case TipKontakta.PHONE:
					self.phone.send_sms(phone=kontakt.data, text=temp.sms_verifikacija)

		# * DODAJ SE MAIN TOKEN NA ZADNJE MESTO!
		tp = TokenPart(order=i, data=token)
		token_parts.append(tp)

		return token_parts
