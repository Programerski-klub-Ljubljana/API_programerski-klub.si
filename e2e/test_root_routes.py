import unittest

from starlette.testclient import TestClient

from api import API


class test_root(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		API.init()
		cls.client = TestClient(API.fapi)

	def test_openapi(self):
		res = self.client.get('/openapi.json')
		body = res.json()
		self.assertIsInstance(body['info'], dict)



if __name__ == '__main__':
	unittest.main()
