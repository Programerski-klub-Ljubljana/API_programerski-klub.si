from enum import auto, Enum

import stripe
from autologging import traced
from stripe.api_resources.customer import Customer
from stripe.api_resources.invoice import Invoice
from stripe.api_resources.transfer import Transfer
from stripe.api_resources.webhook_endpoint import WebhookEndpoint

from app import ENV
from core.services.payment_service import PaymentService


@traced
class Stripe(PaymentService):

	def placilo(self):
		print('placilo')


def init():
	stripe.api_key = ENV.STRIPE_API_KEY


def webhook_create(
		url: str,
		description: str,
		metadata: str):
	"""https://stripe.com/docs/api/webhook_endpoints/create"""
	kwargs = {
		'enabled_events': ['*'],
		**locals()
	}
	WebhookEndpoint.create(**kwargs)


def webhook_get(webhook_id: str):
	"""https://stripe.com/docs/api/webhook_endpoints/retrieve"""
	WebhookEndpoint.get(webhook_id)


def webhook_list():
	"""https://stripe.com/docs/api/webhook_endpoints/list"""
	kwargs = {
		**locals()
	}
	WebhookEndpoint.list(**kwargs)


def webhook_delete(webhook_id: str):
	kwargs = {
		**locals()
	}
	WebhookEndpoint.delete(**kwargs)


def customer_create(
		description,
		email,
		metadata,
		name,
		payment_method,
		phone
):
	"""https://stripe.com/docs/api/customers/create"""
	kwargs = {
		'payment_method': payment_method
		                  ** locals()
	}
	print(Customer.create(description="asdfsdfdf"))


def invoice_create(
		customer_id: str,
		description: str,
		metadata: dict[str, str],
		custom_fields: dict[str, str]):
	"""https://stripe.com/docs/api/invoices/create """
	kwargs = {
		'auto_advance': False,
		'collection_method': 'send_invoice',
		'days_until_due': 14,
		'footer': "TODO: This is footer!",
		**locals()
	}
	Invoice.create(**kwargs)


def invoice_get(invoice_id: str):
	"""https://stripe.com/docs/api/invoices/retrieve"""
	kwargs = {
		**locals()
	}
	return Invoice.retrieve(**locals())


def invoice_finalize(invoice_id: str):
	"""https://stripe.com/docs/api/invoices/finalize"""
	kwargs = {
		**locals()
	}
	return Invoice.finalize_invoice(**locals())


def invoice_send(invoice_id: str):
	"""https://stripe.com/docs/api/invoices/send"""
	kwargs = {
		**locals()
	}
	return Invoice.send_invoice(**locals())


class InvoiceStatus(str, Enum):
	draft = auto()
	open = auto()
	paid = auto()
	uncollectible = auto()
	void = auto()


def invoice_list(
		customer_id: str = None,
		status: InvoiceStatus = None):
	"""https://stripe.com/docs/api/invoices/list"""
	kwargs = {
		'limit': 100,
		**locals()
	}
	Invoice.list(**kwargs)


def invoice_search(
		query: str,
		page: int = None):
	"""https://stripe.com/docs/api/invoices/search"""
	kwargs = {
		'limit': 100,
		**locals()
	}
	return Invoice.search(**kwargs)


class Currency(str, Enum):
	EUR = auto()


def transfer_create(
		description: str,
		account_id: int,
		amount: float,
		metadata: dict[str, str]):
	"""https://stripe.com/docs/api/transfers/create"""
	kwargs = {
		'amount': amount,
		'currency': Currency.EUR,
		'destination': account_id,
		'description': description,
		'metadata': metadata,
		**locals()
	}
	return Transfer.create(**kwargs)


def transfer_get(transfer_id: str):
	kwargs = {
		**locals()
	}
	return Transfer.get(**kwargs)


def transfer_list():
	kwargs = {
		'limit': 100,
		**locals()
	}
	return Transfer.list(**kwargs)

# TODO: Make reports.
# TODO: Make automatic payments
