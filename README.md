# API programerski-klub.si

Server programerskega kluba Ljubljana AKA Monster!

## Instalacija

Odpres pycharm in ti prepozna requirements...
In rečeš da hočeš vse inštalirati.

## Zagon

Server poženeš z ukazom, deluje podobno kot deamon.

```bash
uvicorn api.API:fapi.02_services_tests --host 0.0.0.0
```

## Testing

```bash
coverage run -m unittest discover test
```

```bash
coverage html --omit="*/test*,*/core/services/*"
google-chrome htmlcov/index.html
```

```bash
for i in {1..100} ; do echo "-------------------------$i----------------" && python -m unittest test.02_services_tests.test_payment_service; done
```

## TODO:
V token data probaj posiljati _id entitija, saj bo zmeraj unikaten!

## ERRORS
```
1

FAIL: test_070_create_subscription_already_exists (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 149, in test_070_create_subscription_already_exists
self.assertIsNone(self.service.create_subscription(subscription=self.subscription), msg=i)
AssertionError: StripeSubscription(description='description', prices=['si_N0iumKr0NGSw8Y'], customer='cus_N0iuR0svZ3TsgF', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='ESbJZbdNhrDictX8JQdhLm', id='sub_1MGhT4De7wkrxlBYhSWojJ4l', status='active', currency='eur', start_date=datetime.datetime(2022, 12, 19, 12, 25, 14), created=datetime.datetime(2022, 12, 19, 12, 25, 14), trial_start=None, trial_end=None) is not None : 1

======================================================================
FAIL: test_075_search_subscription (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 156, in test_075_search_subscription
    self.assertEqual(len(subscriptions), 1)
AssertionError: 0 != 1

4

======================================================================
ERROR: test_100_delete_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 185, in test_100_delete_customer
    deleted = self.service.delete_customer(entity_id=self.customer.entity_id, with_tries=True)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 150, in delete_customer
    customer = self.get_customer(entity_id=entity_id, with_tries=with_tries)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 128, in get_customer
    raise Exception(f"Customers with duplicated entity_id: {customers}")
Exception: Customers with duplicated entity_id: [StripeCustomer(entity_id='hPbjYvwWg7zrJUjtjBzrq5', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0iy1plBoCtcdV', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 12, 28, 32)), StripeCustomer(entity_id='hPbjYvwWg7zrJUjtjBzrq5', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0ixL8uXkd7wIX', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 12, 28, 15))]

======================================================================
ERROR: test_110_get_deleted_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 204, in test_110_get_deleted_customer
    sub = self.service.get_customer(entity_id=self.customer.entity_id, with_tries=False)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 128, in get_customer
    raise Exception(f"Customers with duplicated entity_id: {customers}")
Exception: Customers with duplicated entity_id: [StripeCustomer(entity_id='hPbjYvwWg7zrJUjtjBzrq5', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0iy1plBoCtcdV', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 12, 28, 32)), StripeCustomer(entity_id='hPbjYvwWg7zrJUjtjBzrq5', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0ixL8uXkd7wIX', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 12, 28, 15))]

======================================================================
FAIL: test_030_create_customer_already_exists (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 102, in test_030_create_customer_already_exists
    self.assertIsNone(self.service.create_customer(self.customer))
AssertionError: StripeCustomer(entity_id='hPbjYvwWg7zrJUjtjBzrq5', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0iy1plBoCtcdV', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 12, 28, 32)) is not None

======================================================================
FAIL: test_085_search_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 167, in test_085_search_customer
    self.assertEqual(len(customers), 1)
AssertionError: 2 != 1

10

======================================================================
ERROR: test_105_get_canceled_subscription (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 199, in test_105_get_canceled_subscription
    sub = self.service.get_subscription(entity_id=self.subscription.entity_id, with_tries=False)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 196, in get_subscription
    raise Exception(f"Subscription with duplicated entity_id: {subscriptions}")
Exception: Subscription with duplicated entity_id: [StripeSubscription(description='description', prices=['si_N0j5ksIdgKGrk9'], customer='cus_N0j4fXyJTRhLad', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='hC6fkqT4vFN3RZWapD7gcs', id='sub_1MGhdQDe7wkrxlBYjKLKyf5S', status='canceled', currency='eur', start_date=datetime.datetime(2022, 12, 19, 12, 35, 56), created=datetime.datetime(2022, 12, 19, 12, 35, 56), trial_start=None, trial_end=None), StripeSubscription(description='description', prices=['si_N0j5JiW1dQ7I9d'], customer='cus_N0j4fXyJTRhLad', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='hC6fkqT4vFN3RZWapD7gcs', id='sub_1MGhd7De7wkrxlBYE4oYeM2d', status='canceled', currency='eur', start_date=datetime.datetime(2022, 12, 19, 12, 35, 37), created=datetime.datetime(2022, 12, 19, 12, 35, 37), trial_start=None, trial_end=None)]

======================================================================
FAIL: test_070_create_subscription_already_exists (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 149, in test_070_create_subscription_already_exists
    self.assertIsNone(self.service.create_subscription(subscription=self.subscription), msg=i)
AssertionError: StripeSubscription(description='description', prices=['si_N0j5ksIdgKGrk9'], customer='cus_N0j4fXyJTRhLad', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='hC6fkqT4vFN3RZWapD7gcs', id='sub_1MGhdQDe7wkrxlBYjKLKyf5S', status='active', currency='eur', start_date=datetime.datetime(2022, 12, 19, 12, 35, 56), created=datetime.datetime(2022, 12, 19, 12, 35, 56), trial_start=None, trial_end=None) is not None : 1

18

======================================================================
ERROR: test_060_get_subscription (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 703, in urlopen
    httplib_response = self._make_request(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 449, in _make_request
    six.raise_from(e, None)
  File "<string>", line 3, in raise_from
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 444, in _make_request
    httplib_response = conn.getresponse()
  File "/usr/lib/python3.10/http/client.py", line 1374, in getresponse
    response.begin()
  File "/usr/lib/python3.10/http/client.py", line 318, in begin
    version, status, reason = self._read_status()
  File "/usr/lib/python3.10/http/client.py", line 287, in _read_status
    raise RemoteDisconnected("Remote end closed connection without"
http.client.RemoteDisconnected: Remote end closed connection without response

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/requests/adapters.py", line 489, in send
    resp = conn.urlopen(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 787, in urlopen
    retries = retries.increment(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/util/retry.py", line 550, in increment
    raise six.reraise(type(error), error, _stacktrace)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/packages/six.py", line 769, in reraise
    raise value.with_traceback(tb)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 703, in urlopen
    httplib_response = self._make_request(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 449, in _make_request
    six.raise_from(e, None)
  File "<string>", line 3, in raise_from
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 444, in _make_request
    httplib_response = conn.getresponse()
  File "/usr/lib/python3.10/http/client.py", line 1374, in getresponse
    response.begin()
  File "/usr/lib/python3.10/http/client.py", line 318, in begin
    version, status, reason = self._read_status()
  File "/usr/lib/python3.10/http/client.py", line 287, in _read_status
    raise RemoteDisconnected("Remote end closed connection without"
urllib3.exceptions.ProtocolError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 324, in _request_internal
    result = self._thread_local.session.request(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/requests/sessions.py", line 587, in request
    resp = self.send(prep, **send_kwargs)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/requests/sessions.py", line 701, in send
    r = adapter.send(request, **kwargs)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/requests/adapters.py", line 547, in send
    raise ConnectionError(err, request=request)
requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 138, in test_060_get_subscription
    subscription = self.service.get_subscription(entity_id=self.subscription.entity_id, with_tries=True)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 188, in get_subscription
    subscriptions = self.search_subscription(f"metadata['entity_id']:'{entity_id}'")
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 215, in search_subscription
    return [StripeSubscription.parse(**dict(s)) for s in stripe.Subscription.search(query=query, limit=self.page_limit).data]
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/api_resources/subscription.py", line 96, in search
    return cls._search(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/api_resources/abstract/searchable_api_resource.py", line 16, in _search
    return cls._static_request(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/api_resources/abstract/api_resource.py", line 139, in _static_request
    response, api_key = requestor.request(method_, url_, params, headers)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/api_requestor.py", line 119, in request
    rbody, rcode, rheaders, my_api_key = self.request_raw(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/api_requestor.py", line 366, in request_raw
    rcontent, rcode, rheaders = self._client.request_with_retries(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 116, in request_with_retries
    return self._request_with_retries_internal(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 171, in _request_with_retries_internal
    raise connection_error
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 143, in _request_with_retries_internal
    response = self.request(method, url, headers, post_data)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 297, in request
    return self._request_internal(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 354, in _request_internal
    self._handle_request_error(e)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 406, in _handle_request_error
    raise error.APIConnectionError(msg, should_retry=should_retry)
stripe.error.APIConnectionError: Unexpected error communicating with Stripe.  If this problem persists,
let us know at support@stripe.com.

(Network error: ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')))

======================================================================
ERROR: test_100_delete_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 703, in urlopen
    httplib_response = self._make_request(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 449, in _make_request
    six.raise_from(e, None)
  File "<string>", line 3, in raise_from
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 444, in _make_request
    httplib_response = conn.getresponse()
  File "/usr/lib/python3.10/http/client.py", line 1374, in getresponse
    response.begin()
  File "/usr/lib/python3.10/http/client.py", line 318, in begin
    version, status, reason = self._read_status()
  File "/usr/lib/python3.10/http/client.py", line 287, in _read_status
    raise RemoteDisconnected("Remote end closed connection without"
http.client.RemoteDisconnected: Remote end closed connection without response

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/requests/adapters.py", line 489, in send
    resp = conn.urlopen(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 787, in urlopen
    retries = retries.increment(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/util/retry.py", line 550, in increment
    raise six.reraise(type(error), error, _stacktrace)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/packages/six.py", line 769, in reraise
    raise value.with_traceback(tb)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 703, in urlopen
    httplib_response = self._make_request(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 449, in _make_request
    six.raise_from(e, None)
  File "<string>", line 3, in raise_from
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/urllib3/connectionpool.py", line 444, in _make_request
    httplib_response = conn.getresponse()
  File "/usr/lib/python3.10/http/client.py", line 1374, in getresponse
    response.begin()
  File "/usr/lib/python3.10/http/client.py", line 318, in begin
    version, status, reason = self._read_status()
  File "/usr/lib/python3.10/http/client.py", line 287, in _read_status
    raise RemoteDisconnected("Remote end closed connection without"
urllib3.exceptions.ProtocolError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 324, in _request_internal
    result = self._thread_local.session.request(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/requests/sessions.py", line 587, in request
    resp = self.send(prep, **send_kwargs)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/requests/sessions.py", line 701, in send
    r = adapter.send(request, **kwargs)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/requests/adapters.py", line 547, in send
    raise ConnectionError(err, request=request)
requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 190, in test_100_delete_customer
    customer = self.service.get_customer(entity_id=self.customer.entity_id, with_tries=False)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 120, in get_customer
    customers = self.search_customers(f"metadata['entity_id']:'{entity_id}'")
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 147, in search_customers
    return [StripeCustomer.parse(**dict(c)) for c in stripe.Customer.search(query=query, limit=self.page_limit).data]
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/api_resources/customer.py", line 179, in search
    return cls._search(search_url="/v1/customers/search", *args, **kwargs)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/api_resources/abstract/searchable_api_resource.py", line 16, in _search
    return cls._static_request(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/api_resources/abstract/api_resource.py", line 139, in _static_request
    response, api_key = requestor.request(method_, url_, params, headers)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/api_requestor.py", line 119, in request
    rbody, rcode, rheaders, my_api_key = self.request_raw(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/api_requestor.py", line 366, in request_raw
    rcontent, rcode, rheaders = self._client.request_with_retries(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 116, in request_with_retries
    return self._request_with_retries_internal(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 171, in _request_with_retries_internal
    raise connection_error
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 143, in _request_with_retries_internal
    response = self.request(method, url, headers, post_data)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 297, in request
    return self._request_internal(
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 354, in _request_internal
    self._handle_request_error(e)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/stripe/http_client.py", line 406, in _handle_request_error
    raise error.APIConnectionError(msg, should_retry=should_retry)
stripe.error.APIConnectionError: Unexpected error communicating with Stripe.  If this problem persists,
let us know at support@stripe.com.

(Network error: ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')))

25

======================================================================
ERROR: test_100_delete_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 185, in test_100_delete_customer
    deleted = self.service.delete_customer(entity_id=self.customer.entity_id, with_tries=True)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 150, in delete_customer
    customer = self.get_customer(entity_id=entity_id, with_tries=with_tries)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 128, in get_customer
    raise Exception(f"Customers with duplicated entity_id: {customers}")
Exception: Customers with duplicated entity_id: [StripeCustomer(entity_id='7zs4cDh48JKofAvVLq8XoA', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jOrdTdqFTYLp', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 12, 54, 36)), StripeCustomer(entity_id='7zs4cDh48JKofAvVLq8XoA', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jNhkFhw17ZkM', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 12, 54, 16))]

======================================================================
ERROR: test_110_get_deleted_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 204, in test_110_get_deleted_customer
    sub = self.service.get_customer(entity_id=self.customer.entity_id, with_tries=False)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 128, in get_customer
    raise Exception(f"Customers with duplicated entity_id: {customers}")
Exception: Customers with duplicated entity_id: [StripeCustomer(entity_id='7zs4cDh48JKofAvVLq8XoA', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jOrdTdqFTYLp', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 12, 54, 36)), StripeCustomer(entity_id='7zs4cDh48JKofAvVLq8XoA', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jNhkFhw17ZkM', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 12, 54, 16))]

======================================================================
FAIL: test_030_create_customer_already_exists (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 102, in test_030_create_customer_already_exists
    self.assertIsNone(self.service.create_customer(self.customer))
AssertionError: StripeCustomer(entity_id='7zs4cDh48JKofAvVLq8XoA', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jOrdTdqFTYLp', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 12, 54, 36)) is not None

======================================================================
FAIL: test_070_create_subscription_already_exists (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 149, in test_070_create_subscription_already_exists
    self.assertIsNone(self.service.create_subscription(subscription=self.subscription), msg=i)
AssertionError: StripeSubscription(description='description', prices=['si_N0jOca6mcYFNky'], customer='cus_N0jNhkFhw17ZkM', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='7zs4cDh48JKofAvVLq8XoA', id='sub_1MGhvqDe7wkrxlBYt4Des73E', status='active', currency='eur', start_date=datetime.datetime(2022, 12, 19, 12, 54, 58), created=datetime.datetime(2022, 12, 19, 12, 54, 58), trial_start=None, trial_end=None) is not None : 3

======================================================================
FAIL: test_075_search_subscription (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 156, in test_075_search_subscription
    self.assertEqual(len(subscriptions), 1)
AssertionError: 0 != 1

======================================================================
FAIL: test_085_search_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 167, in test_085_search_customer
    self.assertEqual(len(customers), 1)
AssertionError: 2 != 1

30

======================================================================
ERROR: test_100_delete_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 185, in test_100_delete_customer
    deleted = self.service.delete_customer(entity_id=self.customer.entity_id, with_tries=True)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 150, in delete_customer
    customer = self.get_customer(entity_id=entity_id, with_tries=with_tries)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 128, in get_customer
    raise Exception(f"Customers with duplicated entity_id: {customers}")
Exception: Customers with duplicated entity_id: [StripeCustomer(entity_id='Fyv7Ao7MEWSMjSZDNSKaYf', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jUQWsdK3wHzb', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 0, 20)), StripeCustomer(entity_id='Fyv7Ao7MEWSMjSZDNSKaYf', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jTNBUtPHEjHM', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 0, 1))]

======================================================================
ERROR: test_110_get_deleted_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 204, in test_110_get_deleted_customer
    sub = self.service.get_customer(entity_id=self.customer.entity_id, with_tries=False)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 128, in get_customer
    raise Exception(f"Customers with duplicated entity_id: {customers}")
Exception: Customers with duplicated entity_id: [StripeCustomer(entity_id='Fyv7Ao7MEWSMjSZDNSKaYf', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jUQWsdK3wHzb', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 0, 20)), StripeCustomer(entity_id='Fyv7Ao7MEWSMjSZDNSKaYf', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jTNBUtPHEjHM', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 0, 1))]

======================================================================
FAIL: test_030_create_customer_already_exists (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 102, in test_030_create_customer_already_exists
    self.assertIsNone(self.service.create_customer(self.customer))
AssertionError: StripeCustomer(entity_id='Fyv7Ao7MEWSMjSZDNSKaYf', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jUQWsdK3wHzb', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 0, 20)) is not None

======================================================================
FAIL: test_085_search_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 167, in test_085_search_customer
    self.assertEqual(len(customers), 1)
AssertionError: 2 != 1
 
37

======================================================================
ERROR: test_105_get_canceled_subscription (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 199, in test_105_get_canceled_subscription
    sub = self.service.get_subscription(entity_id=self.subscription.entity_id, with_tries=False)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 196, in get_subscription
    raise Exception(f"Subscription with duplicated entity_id: {subscriptions}")
Exception: Subscription with duplicated entity_id: [StripeSubscription(description='description', prices=['si_N0jdOvWMSE9CZc'], customer='cus_N0jcYzkdADgXLD', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='DRrvWxUjv7DAQBjVDPetSD', id='sub_1MGi9oDe7wkrxlBYBhCM9dvS', status='canceled', currency='eur', start_date=datetime.datetime(2022, 12, 19, 13, 9, 24), created=datetime.datetime(2022, 12, 19, 13, 9, 24), trial_start=None, trial_end=None), StripeSubscription(description='description', prices=['si_N0jcIvJL3GpEBY'], customer='cus_N0jcYzkdADgXLD', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='DRrvWxUjv7DAQBjVDPetSD', id='sub_1MGi9WDe7wkrxlBYxHWS0QeZ', status='canceled', currency='eur', start_date=datetime.datetime(2022, 12, 19, 13, 9, 6), created=datetime.datetime(2022, 12, 19, 13, 9, 6), trial_start=None, trial_end=None)]

======================================================================
FAIL: test_070_create_subscription_already_exists (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 149, in test_070_create_subscription_already_exists
    self.assertIsNone(self.service.create_subscription(subscription=self.subscription), msg=i)
AssertionError: StripeSubscription(description='description', prices=['si_N0jdOvWMSE9CZc'], customer='cus_N0jcYzkdADgXLD', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='DRrvWxUjv7DAQBjVDPetSD', id='sub_1MGi9oDe7wkrxlBYBhCM9dvS', status='active', currency='eur', start_date=datetime.datetime(2022, 12, 19, 13, 9, 24), created=datetime.datetime(2022, 12, 19, 13, 9, 24), trial_start=None, trial_end=None) is not None : 3

======================================================================
FAIL: test_075_search_subscription (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 156, in test_075_search_subscription
    self.assertEqual(len(subscriptions), 1)
AssertionError: 0 != 1

======================================================================
FAIL: test_110_get_deleted_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 205, in test_110_get_deleted_customer
    self.assertIsNone(sub)
AssertionError: StripeCustomer(entity_id='DRrvWxUjv7DAQBjVDPetSD', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jcYzkdADgXLD', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 8, 44)) is not None

42

======================================================================
ERROR: test_100_delete_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 185, in test_100_delete_customer
    deleted = self.service.delete_customer(entity_id=self.customer.entity_id, with_tries=True)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 150, in delete_customer
    customer = self.get_customer(entity_id=entity_id, with_tries=with_tries)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 128, in get_customer
    raise Exception(f"Customers with duplicated entity_id: {customers}")
Exception: Customers with duplicated entity_id: [StripeCustomer(entity_id='mmzP2RSfvx24bYZfXVyqqa', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jjDe0CGgOttn', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 15, 21)), StripeCustomer(entity_id='mmzP2RSfvx24bYZfXVyqqa', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jiUgovGf8Csw', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 15))]

======================================================================
ERROR: test_110_get_deleted_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 204, in test_110_get_deleted_customer
    sub = self.service.get_customer(entity_id=self.customer.entity_id, with_tries=False)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 128, in get_customer
    raise Exception(f"Customers with duplicated entity_id: {customers}")
Exception: Customers with duplicated entity_id: [StripeCustomer(entity_id='mmzP2RSfvx24bYZfXVyqqa', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jjDe0CGgOttn', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 15, 21)), StripeCustomer(entity_id='mmzP2RSfvx24bYZfXVyqqa', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jiUgovGf8Csw', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 15))]

======================================================================
FAIL: test_030_create_customer_already_exists (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 102, in test_030_create_customer_already_exists
    self.assertIsNone(self.service.create_customer(self.customer))
AssertionError: StripeCustomer(entity_id='mmzP2RSfvx24bYZfXVyqqa', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jjDe0CGgOttn', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 15, 21)) is not None

======================================================================
FAIL: test_070_create_subscription_already_exists (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 149, in test_070_create_subscription_already_exists
    self.assertIsNone(self.service.create_subscription(subscription=self.subscription), msg=i)
AssertionError: StripeSubscription(description='description', prices=['si_N0jjki50j9Y1gM'], customer='cus_N0jiUgovGf8Csw', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='mmzP2RSfvx24bYZfXVyqqa', id='sub_1MGiFyDe7wkrxlBY7pL1AihW', status='active', currency='eur', start_date=datetime.datetime(2022, 12, 19, 13, 15, 46), created=datetime.datetime(2022, 12, 19, 13, 15, 46), trial_start=None, trial_end=None) is not None : 3

======================================================================
FAIL: test_075_search_subscription (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 156, in test_075_search_subscription
    self.assertEqual(len(subscriptions), 1)
AssertionError: 0 != 1

======================================================================
FAIL: test_085_search_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 167, in test_085_search_customer
    self.assertEqual(len(customers), 1)
AssertionError: 2 != 1

44

======================================================================
FAIL: test_110_get_deleted_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 205, in test_110_get_deleted_customer
    self.assertIsNone(sub)
AssertionError: StripeCustomer(entity_id='EEfegaHjTmFV8nYSjM46zP', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jkHbO1dXV4go', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 17, 9)) is not None

48

======================================================================
ERROR: test_105_get_canceled_subscription (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 199, in test_105_get_canceled_subscription
    sub = self.service.get_subscription(entity_id=self.subscription.entity_id, with_tries=False)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 196, in get_subscription
    raise Exception(f"Subscription with duplicated entity_id: {subscriptions}")
Exception: Subscription with duplicated entity_id: [StripeSubscription(description='description', prices=['si_N0jqJpx71pGSoI'], customer='cus_N0jp6bng7IcM4e', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='4ganXBws3tb8e4jSR5SQmP', id='sub_1MGiMnDe7wkrxlBYIEQ58oc5', status='canceled', currency='eur', start_date=datetime.datetime(2022, 12, 19, 13, 22, 49), created=datetime.datetime(2022, 12, 19, 13, 22, 49), trial_start=None, trial_end=None), StripeSubscription(description='description', prices=['si_N0jqNI1gpiThgy'], customer='cus_N0jp6bng7IcM4e', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='4ganXBws3tb8e4jSR5SQmP', id='sub_1MGiMWDe7wkrxlBYZBr6xTNA', status='canceled', currency='eur', start_date=datetime.datetime(2022, 12, 19, 13, 22, 31), created=datetime.datetime(2022, 12, 19, 13, 22, 31), trial_start=None, trial_end=None)]

======================================================================
FAIL: test_070_create_subscription_already_exists (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 149, in test_070_create_subscription_already_exists
    self.assertIsNone(self.service.create_subscription(subscription=self.subscription), msg=i)
AssertionError: StripeSubscription(description='description', prices=['si_N0jqJpx71pGSoI'], customer='cus_N0jp6bng7IcM4e', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='4ganXBws3tb8e4jSR5SQmP', id='sub_1MGiMnDe7wkrxlBYIEQ58oc5', status='active', currency='eur', start_date=datetime.datetime(2022, 12, 19, 13, 22, 49), created=datetime.datetime(2022, 12, 19, 13, 22, 49), trial_start=None, trial_end=None) is not None : 0

======================================================================
FAIL: test_075_search_subscription (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 156, in test_075_search_subscription
    self.assertEqual(len(subscriptions), 1)
AssertionError: 0 != 1

======================================================================
FAIL: test_110_get_deleted_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 205, in test_110_get_deleted_customer
    self.assertIsNone(sub)
AssertionError: StripeCustomer(entity_id='4ganXBws3tb8e4jSR5SQmP', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jp6bng7IcM4e', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 22, 9)) is not None

49

======================================================================
FAIL: test_110_get_deleted_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 205, in test_110_get_deleted_customer
    self.assertIsNone(sub)
AssertionError: StripeCustomer(entity_id='SZ8yPEwxYBVVFvdZ8gnnaz', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jqoEzaOV4l5Y', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 23, 14)) is not None

50

======================================================================
FAIL: test_110_get_deleted_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 205, in test_110_get_deleted_customer
    self.assertIsNone(sub)
AssertionError: StripeCustomer(entity_id='hADiYXkJohvZr3A7JuxXXQ', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jrqhbBWXD9TP', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 24, 19)) is not None

56

======================================================================
FAIL: test_110_get_deleted_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 205, in test_110_get_deleted_customer
    self.assertIsNone(sub)
AssertionError: StripeCustomer(entity_id='evnaiSyiBeGeCh25Z9bKFn', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0jzcPabh5YulS', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 31, 44)) is not None

57

======================================================================
ERROR: test_105_get_canceled_subscription (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 199, in test_105_get_canceled_subscription
    sub = self.service.get_subscription(entity_id=self.subscription.entity_id, with_tries=False)
  File "/home/urosjarc/vcs/api/venv/lib/python3.10/site-packages/autologging.py", line 1041, in autologging_traced_instancemethod_delegator
    return method(*args, **keywords)
  File "/home/urosjarc/vcs/api/app/services/payment_stripe.py", line 196, in get_subscription
    raise Exception(f"Subscription with duplicated entity_id: {subscriptions}")
Exception: Subscription with duplicated entity_id: [StripeSubscription(description='description', prices=['si_N0k1BzHfgHf259'], customer='cus_N0k01gB8TFyr6K', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='JHhDc5mYyKHULQm9GP3xDk', id='sub_1MGiXWDe7wkrxlBYvvCkauXb', status='canceled', currency='eur', start_date=datetime.datetime(2022, 12, 19, 13, 33, 53), created=datetime.datetime(2022, 12, 19, 13, 33, 53), trial_start=None, trial_end=None), StripeSubscription(description='description', prices=['si_N0k1TGzzTBK7dh'], customer='cus_N0k01gB8TFyr6K', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='JHhDc5mYyKHULQm9GP3xDk', id='sub_1MGiXBDe7wkrxlBY8UNR68BT', status='canceled', currency='eur', start_date=datetime.datetime(2022, 12, 19, 13, 33, 32), created=datetime.datetime(2022, 12, 19, 13, 33, 32), trial_start=None, trial_end=None)]

======================================================================
FAIL: test_070_create_subscription_already_exists (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 149, in test_070_create_subscription_already_exists
    self.assertIsNone(self.service.create_subscription(subscription=self.subscription), msg=i)
AssertionError: StripeSubscription(description='description', prices=['si_N0k1BzHfgHf259'], customer='cus_N0k01gB8TFyr6K', collection_method='send_invoice', days_until_due=7, trial_period_days=0, entity_id='JHhDc5mYyKHULQm9GP3xDk', id='sub_1MGiXWDe7wkrxlBYvvCkauXb', status='active', currency='eur', start_date=datetime.datetime(2022, 12, 19, 13, 33, 53), created=datetime.datetime(2022, 12, 19, 13, 33, 53), trial_start=None, trial_end=None) is not None : 1

60

======================================================================
FAIL: test_110_get_deleted_customer (test.02_services_tests.test_payment_service.test_payment_service)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/urosjarc/vcs/api/test/02_services_tests/test_payment_service.py", line 205, in test_110_get_deleted_customer
    self.assertIsNone(sub)
AssertionError: StripeCustomer(entity_id='Qq7gVBNtvxjWqdBR4LbcqX', name='name', description='description', phone='phone', email='jar.fmf@gmail.com', id='cus_N0k4hD0Nj3GXo0', balance=0, discount=None, delinquent=False, created=datetime.datetime(2022, 12, 19, 13, 36, 52)) is not None

```
