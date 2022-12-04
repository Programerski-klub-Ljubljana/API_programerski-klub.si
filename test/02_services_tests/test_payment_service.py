import unittest

from app import APP
from core.services.payment_service import PaymentService


class test_auth(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service: PaymentService = APP.services.payment()

	def test(self):
		customer = self.service.create_customer('test', 'full_name', 'jar.fmf@gmail.com', 'phone')
		self.assertIsNotNone(customer)
		print(customer)


if __name__ == '__main__':
	unittest.main()
