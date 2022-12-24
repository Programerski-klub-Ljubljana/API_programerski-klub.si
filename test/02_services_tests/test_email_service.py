import unittest
from datetime import datetime
from unittest import IsolatedAsyncioTestCase

from app import APP, CONST


class test_email(IsolatedAsyncioTestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service = APP.services.email()

	def test_check_existance_of_alt_email(self):
		self.assertTrue(self.service.check_existance(CONST.alt_email))

	def test_check_existance_of_email(self):
		self.assertTrue(self.service.check_existance(CONST.email))

	async def test_send(self):
		await self.service.send(
			[CONST.alt_email],
			f'TESTING: {datetime.now()}',
			f'<h3><b>__file__</b> = {__file__}<br><b>__name__</b> = {__name__}</h3>')


if __name__ == '__main__':
	unittest.main()
