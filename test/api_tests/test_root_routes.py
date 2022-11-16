import unittest


class test_root(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		app.init(seed=True)
		api.init()
		cls.client = TestClient(api.api)

	def test_openapi(self):
		res = self.client.get('/openapi.json')
		body = res.json()
		self.assertIsInstance(body['title'], str)



if __name__ == '__main__':
	unittest.main()
