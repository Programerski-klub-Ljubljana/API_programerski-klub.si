import unittest

from app import app


class test_email(unittest.TestCase):

	def setUp(self) -> None:
		app.init(seed=False)
		self.service = app.services.email()

	def test_obstaja_pass(self):
		self.assertTrue(
			self.service.obstaja('jar.fmf@gmail.com')
		)

	def test_obstaja_fail(self):
		self.assertFalse(
			self.service.obstaja('krneki')
		)


if __name__ == '__main__':
	unittest.main()
