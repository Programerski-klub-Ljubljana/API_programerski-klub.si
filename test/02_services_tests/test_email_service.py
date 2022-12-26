import time
import unittest
from datetime import datetime
from unittest import IsolatedAsyncioTestCase

import shortuuid

from app import APP, CONST
from core.services.email_service import EmailService, Email, EmailPerson


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

	async def test_send_and_mailbox(self):
		subject = f'TESTING: {datetime.now()}'
		vsebina = f'<h3><b>__file__</b> = {__file__}<br><b>__name__</b> = {__name__}</h3>'
		await self.service.send(
			recipients=[CONST.emails.api],
			subject=subject,
			vsebina=vsebina)
		send_email = Email(sender=EmailPerson(name=CONST.org_name, email=CONST.emails.api), subject=subject, content=vsebina)
		while True:
			email = self.service.mailbox()[-1]
			if email.subject == send_email.subject:
				self.assertEqual(send_email.sender, EmailPerson(name=CONST.org_name, email=CONST.emails.api))
				self.assertEqual(send_email.content, vsebina)
				break
			time.sleep(1)


if __name__ == '__main__':
	unittest.main()
