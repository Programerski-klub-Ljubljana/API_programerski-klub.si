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

	async def test_send_and_get_all_and_delete(self):
		subject = f'TESTING: {datetime.now()}'
		vsebina = f'<h3><b>__file__</b> = {__file__}<br><b>__name__</b> = {__name__}</h3>'
		await self.service.send(
			recipients=[CONST.emails.api],
			subject=subject,
			vsebina=vsebina)
		send_email = Email(
			sender=EmailPerson(name=CONST.org_name, email=CONST.emails.api),
			subject=subject,
			content=vsebina)

		while True:
			emails = self.service.get_all()
			get_email = emails[-1]
			if send_email.subject == get_email.subject:
				self.assertEqual(send_email.sender, get_email.sender)
				self.assertEqual(send_email.content, get_email.content)
				break
			time.sleep(1)

		self.assertTrue(self.service.delete(id=get_email.id))

	def test_inbox_status(self):
		folder_status = self.service.inbox_status()
		for k, v in folder_status.__dict__.items():
			self.assertGreaterEqual(v, 0, msg=k)

	def test_folder_status(self):
		folder_status = self.service.folder_status(folder='INBOX')
		for k, v in folder_status.__dict__.items():
			self.assertGreaterEqual(v, 0, msg=k)


if __name__ == '__main__':
	unittest.main()
