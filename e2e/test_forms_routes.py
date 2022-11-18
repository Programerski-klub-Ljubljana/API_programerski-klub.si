import unittest

from starlette.testclient import TestClient

from api import API


class test_forms(unittest.TestCase):

	@classmethod
	def setUpClass(cls) -> None:
		API.init()
		cls.client = TestClient(API.fapi)

	def test_vpis(self):
		res = self.client.post('/forms/vpis', data={
			'ime': "Janez",
			'priimek': "Novak",
			'dan_rojstva': 24,
			'mesec_rojstva': 5,
			'leto_rojstva': 1992,
			'email': "jar.fmf@gmail.com",
			'telefon': "+386051240885",
		})
		self.assertGreaterEqual(res.status_code, 200)
		print(res.text)

	# def test_vpis2(self):
	# 	res = self.client.get('/forms/vpis', data={
	# 		'ime': "Janez",
	# 		'priimek': "Novak",
	# 		'dan_rojstva': 24,
	# 		'mesec_rojstva': 5,
	# 		'leto_rojstva': 1992,
	# 		'email': "jar.fmf@gmail.com",
	# 		'telefon': "051240885",
	# 		'ime_skrbnika': "",
	# 		'priimek_skrbnika': "",
	# 		'email_skrbnika': "",
	# 		'telefon_skrbnika': "",
	# 	})
	# 	body = res.json()
	# 	print(body)


if __name__ == '__main__':
	unittest.main()
