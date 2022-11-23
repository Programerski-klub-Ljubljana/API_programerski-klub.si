import unittest

from app import ENV


class test_ENV(unittest.TestCase):
	def test_values(self):
		count = 0
		for k in dir(ENV):
			if not k.startswith('__'):
				count += 1
				val = getattr(ENV, k, False)
				if isinstance(val, int | float | None):
					continue
				self.assertTrue(val, k)
		self.assertGreater(count, 0)


if __name__ == '__main__':
	unittest.main()
