import unittest
from datetime import datetime
from unittest import IsolatedAsyncioTestCase

import shortuuid

from app import APP, CONST


class test_email(IsolatedAsyncioTestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service = APP.services.email()

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


if __name__ == '__main__':
	unittest.main()
