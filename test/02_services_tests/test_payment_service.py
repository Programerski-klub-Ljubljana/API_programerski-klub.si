import unittest
from datetime import datetime, timedelta

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

		cls.customer = Customer(name='name', description='description', billing_email='jar.fmf@gmail.com', languages=['si-SI'])
		cls.customer_fail = Customer(id='xxx', name='name', description='description', billing_email='xxx', languages=['si-SI'])
		cls.subscription = Subscription(
			description='description', prices=cls.prices,
			customer=cls.customer, collection_method=CollectionMethod.SEND_INVOICE,
			days_until_due=7, trial_period_days=0)

	def assertEqualCustomer(self, res_c, original):
		if original.id is not None:
			self.assertEqual(res_c.id, original.id)

		for k, v in original.__dict__.items():
			if v is not None:
				self.assertEqual(v, res_c.__dict__[k], k)
			elif k not in ['discount']:
				self.assertIsNotNone(res_c.__dict__[k], k)

		return True

	def assertEqualSubscription(self, res_s, original):
		self.assertEqual(res_s.customer.id, original.customer.id)
		self.assertEqual(len(res_s.prices), len(original.prices))
		if original.id is not None:
			self.assertEqual(res_s.id, original.id)

		for k, v in original.__dict__.items():
			if v is not None and k not in ['id', 'customer', 'prices']:
				self.assertEqual(v, res_s.__dict__[k])
			elif k not in ['trial_start', 'trial_end', 'canceled_at']:
				self.assertIsNotNone(res_s.__dict__[k], msg=k)

		return True

	def assertCustomerIn(self, customers, customer):
		ids = [c.id for c in customers]
		found_customer = customers[ids.index(customer.id)]
		self.assertEqualCustomer(found_customer, customer)

	def assertSubscriptionIn(self, subscriptions, subscription):
		ids = [s.id for s in subscriptions]
		found_subscription = subscriptions[ids.index(subscription.id)]
		self.assertEqualSubscription(found_subscription, subscription)


class test_customer(test_payment_service):
	"""CREATE CUSTOMERS =========================================================== """

	def test_01_create_customer_wrong_email(self):
		customer = self.service.create_customer(self.customer_fail)
		self.assertIsNone(customer)

	def test_02_create_customer(self):
		before = datetime.now() - timedelta(seconds=1)
		customer = self.service.create_customer(self.customer)
		after = datetime.now() + timedelta(seconds=1)

		self.assertTrue(before.timestamp() - 10 <= customer.created.timestamp() <= after.timestamp() + 10)
		self.assertEqualCustomer(customer, self.customer)
		test_customer.customer = customer

	""" GET CUSTOMERS """

	def test_03_get_customer(self):
		customer = self.service.get_customer(id=self.customer.id)
		self.assertEqual(customer.id, self.customer.id)
		self.assertEqualCustomer(customer, self.customer)

	def test_03_get_customer_not_exists(self):
		customer = self.service.get_customer(id='xxx')
		self.assertIsNone(customer)

	""" LIST CUSTOMERS """

	def test_04_list_customers(self):
		customers = self.service.list_customers()
		self.assertCustomerIn(customers, self.customer)

	""" DELETE CUSTOMER """

	def test_05_delete_customer_not_exists(self):
		deleted = self.service.delete_customer(id='xxx')
		self.assertFalse(deleted)

	def test_05_delete_customer(self):
		deleted = self.service.delete_customer(id=self.customer.id)
		self.assertTrue(deleted)

	""" CHECK IF CUSTOMER IS REALLY IS DELETED """

	def test_07_get_deleted_customer(self):
		customer = self.service.get_customer(id=self.customer.id)
		self.assertIsNone(customer)


class test_subscription(test_payment_service):
	""" CREATE SUBSCRIPTIONS ======================================================= """

	def test_01_create_subscription_unknown_customer(self):
		self.assertIsNone(self.service.create_subscription(
			subscription=Subscription(
				description='desciption', prices=self.prices,
				customer=self.customer_fail, collection_method=CollectionMethod.SEND_INVOICE,
				days_until_due=7, trial_period_days=7)))

	def test_02_create_subscription_unknown_price(self):
		self.assertIsNone(self.service.create_subscription(
			subscription=Subscription(
				description='desciption', prices=['xxx'],
				customer=self.service.create_customer(self.customer),
				collection_method=CollectionMethod.SEND_INVOICE,
				days_until_due=7, trial_period_days=7)))

	def test_030_create_subscription(self):
		self.subscription.customer = self.service.create_customer(self.customer)
		sub = self.service.create_subscription(subscription=self.subscription)
		self.assertEqualSubscription(sub, self.subscription)
		test_subscription.subscription = sub

	def test_031_test_id(self):
		self.assertIsNotNone(self.subscription.id)
		self.assertIsNotNone(self.subscription.customer.id)

	""" GET SUBSCRIPTION """

	def test_04_get_subscription(self):
		subscription = self.service.get_subscription(id=self.subscription.id)
		self.assertNotEqual(subscription.status, SubscriptionStatus.CANCELED)
		self.assertIsNotNone(subscription)
		self.assertEqualSubscription(subscription, self.subscription)

	def test_05_get_customer_subscriptions(self):
		subscription = self.service.get_subscription(id=self.subscription.id)
		customer = self.service.get_customer(id=self.subscription.customer.id)
		self.assertEqual(customer.subscriptions, [subscription])

	def test_06_check_if_customers_has_subscriptions(self):
		subscription = self.service.get_subscription(id=self.subscription.id)
		customers = self.service.list_customers()
		for c in customers:
			if c.id == self.customer.id:
				self.assertEqual(c.subscriptions, [subscription])

	def test_07_get_subscription_not_exists(self):
		self.assertIsNone(self.service.get_subscription(id='xxx'))

	def test_08_cancel_subscription_not_exists(self):
		self.assertFalse(self.service.cancel_subscription(id='xxx'))

	""" LIST SUBSCRIPTIONS """

	def test_09_list_subscription(self):
		subscriptions = self.service.list_subscriptions()
		self.assertSubscriptionIn(subscriptions, self.subscription)

	""" CANCEL SUBSCRIPTION """

	def test_10_cancel_subscription(self):
		deleted = self.service.cancel_subscription(id=self.subscription.id)
		self.assertTrue(deleted)

		subscription = self.service.get_subscription(id=self.subscription.id)
		self.assertEqual(subscription.status, SubscriptionStatus.CANCELED)

	""" CHECK IF SUBSCRIPTION IS REALLY IS DELETED """

	def test_11_get_canceled_subscription(self):
		now = datetime.today()
		subscription = self.service.get_subscription(id=self.subscription.id)
		self.assertIsNotNone(subscription)
		self.assertEqual(subscription.status, SubscriptionStatus.CANCELED)
		self.assertLess(subscription.canceled_at, now)


if __name__ == '__main__':
	unittest.main()
