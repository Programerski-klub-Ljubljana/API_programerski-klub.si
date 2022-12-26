import unittest
from datetime import datetime
from unittest import IsolatedAsyncioTestCase

import shortuuid

from app import APP, CONST
from core.services.email_service import EmailService


class test_email(IsolatedAsyncioTestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service: EmailService = APP.services.email()

	def test_check_existance_of_email(self):
		for k, v in CONST.emails.__dict__.items():
			if not k.startswith('__') and isinstance(v, str):
				self.assertTrue(self.service.check_existance(v), msg=k)

		self.assertFalse(self.service.check_existance('xxx'))
		self.assertFalse(self.service.check_existance(f'xxx@{shortuuid.uuid().lower()}.com'))

	async def test_send(self):
		await self.service.send(
			[CONST.emails.api],
			f'TESTING: {datetime.now()}',
			f'<h3><b>__file__</b> = {__file__}<br><b>__name__</b> = {__name__}</h3>')

	def test_mailbox(self):
		email = self.service.mailbox()[-1]
		self.assertTrue(self.service.check_existance(email.sender.email))
		self.assertGreater(len(email.sender.name), 3)
		self.assertGreater(len(email.subject), 2)
		self.assertIsNotNone(email.content)


if __name__ == '__main__':
	unittest.main()
