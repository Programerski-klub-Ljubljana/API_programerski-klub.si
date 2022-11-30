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

	def test_equal(self):
		self.assertNotEqual('FakeEnum.NAME', FakeEnum.NAME)
		self.assertEqual('FakeEnum.NAME', str(FakeEnum.NAME))


if __name__ == '__main__':
	unittest.main()
