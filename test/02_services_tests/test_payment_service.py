import time
import unittest
from datetime import datetime, timedelta

import shortuuid

from app import APP
from core.services.payment_service import PaymentService, Customer, Subscription, CollectionMethod, SubscriptionStatus


class test_payment_service(unittest.TestCase):
	prices = None
	customer = None
	subscription = None

	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service: PaymentService = APP.services.payment()
		cls.prices = ["klubska_clanarina"]

		cls.customer = Customer(entity_id=shortuuid.uuid(), name='name', description='description', phone='phone', email='jar.fmf@gmail.com')
		cls.customer_fail = Customer(entity_id="entity_id1", name='name', description='description', phone='phone', email='xxx')
		cls.subscription = Subscription(
			entity_id=cls.customer.entity_id,
			description='description',
			prices=cls.prices,
			customer=cls.customer, collection_method=CollectionMethod.SEND_INVOICE,
			days_until_due=7, trial_period_days=0)

	def assertEqualCustomer(self, res_c, original):
		self.assertEqual(original.entity_id, res_c.entity_id)
		self.assertGreater(len(res_c.id), 3)
		self.assertIsNone(original.id)
		self.assertIsNone(original.created)

		for k, v in original.__dict__.items():
			if v is not None:
				self.assertEqual(v, res_c.__dict__[k])
			elif k not in ['discount']:
				self.assertIsNotNone(res_c.__dict__[k])

		return True

	def assertEqualSubscription(self, res_s, original):
		self.assertGreater(len(res_s.id), 3)
		self.assertIsNone(original.id)
		self.assertIsNone(original.created)

		for k, v in original.__dict__.items():
			if v is not None and k not in ['id', 'prices', 'customer']:
				self.assertEqual(v, res_s.__dict__[k])
			elif k not in ['trial_start', 'trial_end']:
				self.assertIsNotNone(res_s.__dict__[k], msg=k)

		return True

	def assertCustomerIn(self, customers, customer):
		ids = [c.entity_id for c in customers]
		found_customer = customers[ids.index(customer.entity_id)]
		self.assertEqualCustomer(found_customer, customer)

	def assertSubscriptionIn(self, subscriptions, subscription):
		ids = [s.entity_id for s in subscriptions]
		found_subscription = subscriptions[ids.index(subscription.entity_id)]
		self.assertEqualSubscription(found_subscription, subscription)

	""" CUSTOMERS """

	def test_000_create_customer(self):
		before = datetime.now() - timedelta(seconds=1)
		customer = self.service.create_customer(self.customer)
		after = datetime.now() + timedelta(seconds=1)

		self.assertTrue(before.timestamp() - 10 <= customer.created.timestamp() <= after.timestamp() + 10)
		self.assertEqualCustomer(customer, self.customer)

	def test_005_get_customer_not_exists(self):
		customer = self.service.get_customer(entity_id='xxx', with_tries=False)
		self.assertIsNone(customer)

	def test_010_delete_customer_not_exists(self):
		deleted = self.service.delete_customer(entity_id='xxx', with_tries=False)
		self.assertFalse(deleted)

	def test_015_create_customer_wrong_email(self):
		customer = self.service.create_customer(self.customer_fail)
		self.assertIsNone(customer)

	def test_020_get_customer(self):
		customer = self.service.get_customer(entity_id=self.customer.entity_id)
		self.assertEqualCustomer(customer, self.customer)

	def test_025_list_customers(self):
		customers = self.service.list_customers()
		self.assertCustomerIn(customers, self.customer)

	def test_030_create_customer_already_exists(self):
		self.assertIsNone(self.service.create_customer(self.customer))

	""" SUBSCRIPTIONS """

	def test_035_create_subscription(self):
		customer = self.service.get_customer(entity_id=self.customer.entity_id)
		self.subscription.customer = customer
		sub = self.service.create_subscription(subscription=self.subscription)
		self.assertEqualSubscription(sub, self.subscription)

	def test_040_create_subscription_unknown_customer(self):
		customer = self.customer_fail
		customer.id = 'xxx'
		self.assertIsNone(self.service.create_subscription(
			subscription=Subscription(
				description='desciption',
				prices=self.prices,
				customer=customer, collection_method=CollectionMethod.SEND_INVOICE,
				days_until_due=7, trial_period_days=7)))

	def test_045_create_subscription_unknown_price(self):
		customer = self.service.get_customer(entity_id=self.customer.entity_id)
		self.assertIsNone(self.service.create_subscription(
			subscription=Subscription(
				description='desciption',
				prices=['xxx'],
				customer=customer, collection_method=CollectionMethod.SEND_INVOICE,
				days_until_due=7, trial_period_days=7)))

	def test_050_get_subscription_not_exists(self):
		self.assertIsNone(self.service.get_subscription(entity_id='xxx', with_tries=False))

	def test_055_cancel_subscription_not_exists(self):
		self.assertFalse(self.service.cancel_subscription(entity_id='xxx', with_tries=False))

	def test_060_get_subscription(self):
		subscription = self.service.get_subscription(entity_id=self.subscription.entity_id, with_tries=True)
		self.assertNotEqual(subscription.status, SubscriptionStatus.CANCELED)
		self.assertIsNotNone(subscription)
		self.assertEqualSubscription(subscription, self.subscription)

	def test_065_list_subscription(self):
		subscriptions = self.service.list_subscriptions()
		self.assertSubscriptionIn(subscriptions, self.subscription)

	def test_070_create_subscription_already_exists(self):
		sub = self.service.create_subscription(subscription=self.subscription)
		self.assertIsNone(sub)

	""" SEARCHING SUBSCRIPTION """

	def test_075_search_subscription(self):
		subscriptions = self.service.search_subscription(query=f"metadata['entity_id']:'{self.subscription.entity_id}' AND -status:'canceled'")
		self.assertEqual(len(subscriptions), 1)
		self.assertEqualSubscription(subscriptions[0], self.subscription)

	def test_080_search_subscription_not_found(self):
		subscriptions = self.service.search_subscription(query=f"metadata['entity_id']:'xxx'")
		self.assertEqual(len(subscriptions), 0)

	""" SEARCHING CUSTOMER """

	def test_085_search_customer(self):
		customers = self.service.search_customers(query=f"metadata['entity_id']:'{self.customer.entity_id}'")
		self.assertEqual(len(customers), 1)
		self.assertEqualCustomer(customers[0], self.customer)

	def test_090_search_customer_not_found(self):
		customers = self.service.search_customers(query=f"metadata['entity_id']:'xxx'")
		self.assertEqual(len(customers), 0)

	def test_095_cancel_subscription(self):
		subscription = self.service.get_subscription(entity_id=self.subscription.entity_id, with_tries=False)
		self.assertEqual(subscription.status, SubscriptionStatus.ACTIVE)

		deleted = self.service.cancel_subscription(entity_id=self.subscription.entity_id, with_tries=False)
		self.assertTrue(deleted)

		subscription = self.service.get_subscription(entity_id=self.subscription.entity_id, with_tries=False)
		self.assertEqual(subscription.status, SubscriptionStatus.CANCELED)

	def test_100_delete_customer(self):
		deleted = self.service.delete_customer(entity_id=self.customer.entity_id, with_tries=True)
		self.assertTrue(deleted)

		c = 20
		while c > 0:
			customer = self.service.get_customer(entity_id=self.customer.entity_id, with_tries=False)
			c -= 1
			if customer is None:
				return None
			time.sleep(1)

		raise Exception("Is not really deleted!")

	def test_105_get_canceled_subscription(self):
		sub = self.service.get_subscription(entity_id=self.subscription.entity_id, with_tries=False)
		self.assertIsNone(sub)

	def test_110_get_celeted_customer(self):
		sub = self.service.get_customer(entity_id=self.customer.entity_id, with_tries=False)
		self.assertIsNone(sub)

if __name__ == '__main__':
	unittest.main()
