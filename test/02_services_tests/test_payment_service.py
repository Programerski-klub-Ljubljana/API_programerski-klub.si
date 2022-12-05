import time
import unittest
from datetime import datetime, timedelta

from app import APP
from core.services.payment_service import PaymentService, PaymentCustomer


class test_auth(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service: PaymentService = APP.services.payment()
		cls.customer = PaymentCustomer(entity_id="entity_id", name='name', description='desciption', phone='phone', email='jar.fmf@gmail.com')

	def assertEqualCustomer(self, res_c, original):
		self.assertEqual(original.entity_id, res_c.entity_id)
		self.assertGreater(len(res_c.id), 3)
		self.assertIsNone(original.id)
		self.assertIsNone(original.created)
		res_c.id = original.id
		res_c.created = original.created
		self.assertEqual(original, res_c)

	def test_00_create_customer(self):
		before = datetime.utcnow() - timedelta(seconds=1)
		customer = self.service.create_customer(self.customer)
		after = datetime.utcnow() + timedelta(seconds=1)

		self.assertTrue(before.timestamp() - 1000 <= customer.created.timestamp() <= after.timestamp() + 1000)
		self.assertEqualCustomer(customer, self.customer)

	def test_01_get_customer(self):
		customer = self.service.get_customer(entity_id=self.customer.entity_id)
		self.assertEqualCustomer(customer, self.customer)

	def test_02_list_customers(self):
		customers = self.service.list_customers()
		count = 0
		for c in customers:
			if c.entity_id == self.customer.entity_id:
				self.assertEqualCustomer(c, self.customer)
				count += 1
		self.assertEqual(count, 1)

	def test_03_delete_customer(self):
		deleted = self.service.delete_customer(entity_id=self.customer.entity_id)
		self.assertTrue(deleted)
		self.assertListEqual([], self.service.list_customers())


if __name__ == '__main__':
	unittest.main()
