import unittest

from app import APP


class test_email(unittest.TestCase):


	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service = APP.services.email()

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
