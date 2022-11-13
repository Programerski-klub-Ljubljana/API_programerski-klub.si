import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

from app import app
from core import utils
from core.domain.arhitektura_kluba import Clan, Kontakt
from core.services.email_service import EmailService
from core.services.sms_service import SmsService
from core.use_cases.validation import ValidateClan, ValidateKontakt


class test_validate(unittest.TestCase):

	def setUp(self) -> None:
		pass

	def test_root_path(self):
		result = utils.root_path('api')
		self.assertEqual(result, Path('../api').resolve().absolute())

	def test_age(self):
		today = datetime.utcnow()
		self.assertEqual(12.5027, round(utils.age(today.year-12, today.month-6, today.day-1),4))

	def test_is_iterable(self):
		self.assertTrue(utils.is_iterable([]))
		self.assertTrue(utils.is_iterable({}))


if __name__ == '__main__':
	unittest.main()
