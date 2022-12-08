import unittest
from datetime import datetime, timedelta

from app import APP
from core.services.payment_service import PaymentService, Customer, Subscription, CollectionMethod


class test_customer(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service: PaymentService = APP.services.payment()
		cls.customer = Customer(entity_id="entity_id0", name='name', description='desciption', phone='phone', email='jar.fmf@gmail.com')
		cls.customer_fail = Customer(entity_id="entity_id1", name='name', description='desciption', phone='phone', email='xxx')

	def assertEqualCustomer(self, res_c, original):
		self.assertEqual(original.entity_id, res_c.entity_id)
		self.assertGreater(len(res_c.id), 3)
		self.assertIsNone(original.id)
		self.assertIsNone(original.created)
		res_c.id = original.id
		res_c.created = original.created
		res_c.balance = original.balance
		res_c.delinquent = original.delinquent
		self.assertEqual(original.__dict__, res_c.__dict__)

	def test_00_create_customer(self):
		before = datetime.now() - timedelta(seconds=1)
		customer = self.service.create_customer(self.customer)
		after = datetime.now() + timedelta(seconds=1)

		self.assertTrue(before.timestamp() <= customer.created.timestamp() <= after.timestamp())
		self.assertEqualCustomer(customer, self.customer)

	def test_01_get_customer_not_exists(self):
		customer = self.service.get_customer(entity_id='xxx', with_tries=False)
		self.assertIsNone(customer)

	def test_02_delete_customer_not_exists(self):
		deleted = self.service.delete_customer(entity_id='xxx', with_tries=False)
		self.assertFalse(deleted)

	def test_03_create_customer_fail(self):
		customer = self.service.create_customer(self.customer_fail)
		self.assertIsNone(customer)

	def test_04_get_customer(self):
		customer = self.service.get_customer(entity_id=self.customer.entity_id)
		self.assertEqualCustomer(customer, self.customer)

	def test_05_list_customers(self):
		customers = self.service.list_customers()
		count = 0
		for c in customers:
			if c.entity_id == self.customer.entity_id:
				self.assertEqualCustomer(c, self.customer)
				count += 1
		self.assertEqual(count, 1)

	def test_06_create_subscription(self):
		customer = self.service.get_customer(entity_id=self.customer.entity_id)
		sub = Subscription(
			entity_id='entity_id',
			description='desciption',
			items=["price_1MC13kDe7wkrxlBY9OUlLuMX"],
			customer=customer, collection_method=CollectionMethod.SEND_INVOICE,
			days_until_due=7, trial_period_days=7
		)
		sub = self.service.create_subscription(sub)
		print(sub)

	def test_delete_customer(self):
		deleted = self.service.delete_customer(entity_id=self.customer.entity_id)
		self.assertTrue(deleted)
		self.assertListEqual([], self.service.list_customers())


if __name__ == '__main__':
	unittest.main()
