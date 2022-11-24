import unittest

from app import APP


class test_email(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service = APP.services.email()

	def test_obstaja(self):
		self.assertTrue(self.service.obstaja('jar.fmf@gmail.com'))

	def test_send(self):
		# with todo: you stayed here!
		self.service.send(['jar.fmf@gmail.com'], 'subject', 'vsebina')



if __name__ == '__main__':
	unittest.main()
