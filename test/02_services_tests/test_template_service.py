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
			temp.web_napaka
		except UndefinedError as err:
			self.assertEqual(str(err), "'ime' is undefined")

	def test_success(self):
		temp = self.service.init(priimek='priimek')
		temp('ime', 'ime')
		temp('napake', ['napaka1', 'napaka2'])
		self.assertIn("</body>", temp.web_napaka)


if __name__ == '__main__':
	unittest.main()
