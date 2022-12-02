import unittest
from enum import auto

from core.domain._enums import EntityEnum


class FakeEnum(EntityEnum):
	NAME = auto()
	SURNAME = auto()
	AGE = auto()
	COUNTRY = auto()


class test_Elist(unittest.TestCase):
	def test_values(self):
		self.assertCountEqual(FakeEnum.values(), [FakeEnum.NAME, FakeEnum.SURNAME, FakeEnum.AGE, FakeEnum.COUNTRY])

	def test_random(self):
		rand = [FakeEnum.random() for _ in range(20)]
		self.assertNotEqual(rand.count(rand[0]), 0)

	def test_eq(self):
		self.assertNotEqual('FakeEnum.NAME', FakeEnum.NAME)
		self.assertEqual('FakeEnum.NAME', str(FakeEnum.NAME))

	def test_equal(self):
		self.assertTrue(FakeEnum.NAME.equal(FakeEnum.NAME))
		self.assertFalse(FakeEnum.NAME.equal(FakeEnum.AGE))

	def test_comparisons(self):
		self.assertLess(FakeEnum.NAME, FakeEnum.SURNAME)
		self.assertLess(FakeEnum.NAME, FakeEnum.AGE)
		self.assertLess(FakeEnum.NAME, FakeEnum.COUNTRY)

		self.assertLess(FakeEnum.SURNAME, FakeEnum.AGE)
		self.assertLess(FakeEnum.SURNAME, FakeEnum.COUNTRY)

		self.assertRaises(Exception, lambda: FakeEnum.AGE < "asdf")


if __name__ == '__main__':
	unittest.main()
