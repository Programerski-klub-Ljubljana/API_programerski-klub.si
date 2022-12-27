import unittest
from unittest.mock import MagicMock

from app import APP, CONST
from core.domain.arhitektura_kluba import Kontakt, TipKontakta, NivoValidiranosti
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.use_cases.auth_cases import TokenPart
from test.tutils import AsyncMock


class test_TokenPart(unittest.IsolatedAsyncioTestCase):
	def setUp(self) -> None:
		self.token_parts = [
			TokenPart(order=3, data='data3', info='info3'),
			TokenPart(order=1, data='data1', info='info1'),
			TokenPart(order=5, data='data5', info='info5'),
			TokenPart(order=2, data='data2', info='info2'),
			TokenPart(order=0, data='data0', info='info0'),
			TokenPart(order=4, data='data4', info='info4')]

	def test_merge(self):
		token = TokenPart.merge(self.token_parts)
		self.assertEqual(token, ''.join([f'data{i}' for i in range(5, -1, -1)]))


class test_send_token_parts(unittest.IsolatedAsyncioTestCase):
	def setUp(self) -> None:
		APP.init(seed=False)

		self.phone_service: PhoneService = MagicMock(PhoneService)
		self.email_service: EmailService = AsyncMock(EmailService)

		self.case = APP.cases.send_token_parts(phone=self.phone_service, email=self.email_service)
		self.token = 'abcdefghijklmnoprstuvz0123456789'
		self.kontakti = [
			Kontakt(data='data0', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.POTRJEN),
			Kontakt(data='data1', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='data2', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.VALIDIRAN),
			Kontakt(data='data3', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.POTRJEN),
			Kontakt(data='data4', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='data5', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.VALIDIRAN)]
		self.token_parts = [
			TokenPart(order=0, data='6789', info='data0'),
			TokenPart(order=1, data='2345', info='data1'),
			TokenPart(order=2, data='vz01', info='data2'),
			TokenPart(order=3, data='rstu', info='data3'),
			TokenPart(order=4, data='mnop', info='data4'),
			TokenPart(order=5, data='ijkl', info='data5'),
			TokenPart(order=6, data='abcdefgh', info=None)]

	async def test_normalna_uporaba(self):
		token_parts = await self.case.exe(self.token, kontakti=self.kontakti)
		self.assertEqual(token_parts, self.token_parts)

		# * TOKEN CAN BE MERGED BACK TOGETHER
		self.assertEqual(TokenPart.merge(token_parts), self.token)

		# * PHONE SERVICE IS CALLED
		call_args = self.phone_service.send_sms.call_args_list
		for count, i in enumerate(range(3, 6)):
			self.assertEqual(list(call_args[count].kwargs.keys()), ['phone', 'text'])
			self.assertEqual(call_args[count].kwargs['phone'], self.kontakti[i].data)
			self.assertIn(token_parts[i].data, call_args[count].kwargs['text'])

		# * EMAIL SERVICE IS CALLED
		call_args = list(self.email_service.send.call_args_list)
		for i in range(3):
			self.assertEqual(list(call_args[i].kwargs.keys()), ['recipients', 'subject', 'vsebina'])
			self.assertEqual(call_args[i].kwargs['recipients'], [self.kontakti[i].data])
			self.assertIn(call_args[i].kwargs['subject'], CONST.email_subject.verifikacija)
			self.assertIn(token_parts[i].data, call_args[i].kwargs['vsebina'])


if __name__ == '__main__':
	unittest.main()
