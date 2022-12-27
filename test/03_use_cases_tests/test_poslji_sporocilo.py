import unittest
from unittest.mock import MagicMock, AsyncMock, call

from app import APP
from core.domain.arhitektura_kluba import Kontakt, NivoValidiranosti, TipKontakta, Oseba
from core.domain.oznanila_sporocanja import Sporocilo
from core.services.email_service import EmailService
from core.services.phone_service import PhoneService
from core.use_cases.msg_cases import Poslji_sporocilo_kontaktu


class test_poslji_sporocilo(unittest.IsolatedAsyncioTestCase):
	kontakti = None
	email = None
	phone = None
	oseba = None
	case = None

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)

		cls.kontakti = [
			Kontakt(data='email0', tip=TipKontakta.EMAIL, nivo_validiranosti=NivoValidiranosti.NI_VALIDIRAN),
			Kontakt(data='phone2', tip=TipKontakta.PHONE, nivo_validiranosti=NivoValidiranosti.POTRJEN)
		]
		cls.oseba = Oseba(ime='ime', priimek='priimek', rojen=None, kontakti=cls.kontakti)

		cls.phone = MagicMock(PhoneService)
		cls.email = MagicMock(EmailService)
		cls.email.send = AsyncMock()
		cls.case: Poslji_sporocilo_kontaktu = APP.cases.poslji_sporocilo(phone=cls.phone, email=cls.email)

		# DB
		with cls.case.db.transaction() as root:
			root.sporocilo.clear()
			root.oseba.clear()
			root.save(cls.oseba)

	@classmethod
	def tearDownClass(cls) -> None:
		with cls.case.db.transaction() as root:
			root.sporocilo.clear()
			root.oseba.clear()

	async def test_je_poslano(self):
		spor = []
		for i, k in enumerate(self.kontakti):
			await self.case.exe(kontakt=k, naslov=f'naslov{i}', vsebina=f'vsebina{i}')
			spor.append(Sporocilo(naslov=f'naslov{i}', vsebina=f'vsebina{i}'))

		self.assertCountEqual(self.email.send.call_args_list, [call(recipients=['email0'], subject='naslov0', vsebina='vsebina0')])
		self.assertCountEqual(self.phone.send_sms.call_args_list, [call(phone='phone2', text='vsebina1')])

		with self.case.db.transaction() as root:
			self.assertCountEqual(root.sporocilo, spor)
			for i, k in enumerate(root.oseba[0].kontakti):
				self.assertEqual(len(k._connections), 1)
				self.assertCountEqual(k._connections, [spor[i]])


if __name__ == '__main__':
	unittest.main()
