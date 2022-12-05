import time
import unittest
from datetime import datetime, timedelta

import stripe

from app import APP
from core.services.payment_service import PaymentService, PaymentCustomer


class test_auth(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service: PaymentService = APP.services.payment()
		cls.customer = PaymentCustomer(entity_id="entity_id", name='name', description='desciption', phone='phone', email='jar.fmf@gmail.com')

	def tearDown(self) -> None:
		time.sleep(2)

	def assertEqualCustomer(self, res_c, original):
		self.assertEqual(original.entity_id, res_c.entity_id)
		self.assertGreater(len(res_c.id), 3)
		self.assertIsNone(original.id)
		self.assertIsNone(original.created)
		res_c.id = original.id
		res_c.created = original.created
		self.assertEqual(original, res_c)

	def test_create_customer(self):
		before = datetime.utcnow() - timedelta(seconds=1)
		customer = self.service.create_customer(self.customer)
		after = datetime.utcnow() + timedelta(seconds=1)

		self.assertTrue(before <= customer.created <= after)
		self.assertEqualCustomer(customer, self.customer)

	def test_list_customers(self):
		customers = self.service.list_customers()
		count = 0
		for c in customers:
			if c.entity_id == self.customer.entity_id:
				self.assertEqualCustomer(c, self.customer)
				count += 1
		self.assertEqual(count, 1)

	def test_get_customer(self):
		time.sleep(3)
		customer = self.service.get_customer(entity_id=self.customer.entity_id)
		self.assertEqualCustomer(customer, self.customer)

	def test_delete_customer(self):
		customer = self.service.delete_customer(entity_id=self.customer.entity_id)
		print(customer)
		# self.assertEqualCustomer(customer, self.customer)
		self.assertListEqual([], self.service.list_customers())


if __name__ == '__main__':
	unittest.main()
