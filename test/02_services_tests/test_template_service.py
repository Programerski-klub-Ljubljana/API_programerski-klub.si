import unittest

from jinja2 import UndefinedError

from app import APP


class test_template(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		APP.init(seed=False)
		cls.service = APP.services.template()

	def test_fail(self):
		temp = self.service.init()
		try:
			temp._TEST
		except UndefinedError as err:
			self.assertEqual(str(err), "'ime' is undefined")

	def test_success(self):
		temp = self.service.init(priimek='priimek')
		temp.set(ime='ime')
		temp.set(napake=['napaka1', 'napaka2'])
		self.assertIn('ime', temp._TEST)
		self.assertIn('napaka1', temp._TEST)
		self.assertIn('napaka2', temp._TEST)


if __name__ == '__main__':
	unittest.main()
