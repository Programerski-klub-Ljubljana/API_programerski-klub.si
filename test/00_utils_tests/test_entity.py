import unittest
from dataclasses import Field, dataclass
from datetime import datetime
from typing import Callable

from core.domain._entity import Elist, Entity, elist

@dataclass
class E(Entity):
	value: int

class test_Elist(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.elist_100 = Elist([E(value=i) for i in range(10000)])
		cls.elist = Elist([E(value=i) for i in range(6)])
		cls.elist_empty = Elist([])

	def test_contains(self):
		self.assertTrue(1 not in self.elist_empty)
		self.assertTrue(None not in self.elist_empty)
		for i in range(10):
			if i <= 5:
				self.assertTrue(E(value=i) in self.elist)
			else:
				self.assertTrue(E(value=i) not in self.elist)

	def test_append_pop(self):
		self.assertEqual(len(self.elist_empty), 0)
		self.elist_empty.append(123)
		self.assertEqual(self.elist_empty[-1], 123)
		self.assertEqual(len(self.elist_empty), 1)
		self.elist_empty.pop(0)
		self.assertEqual(len(self.elist_empty), 0)

	def test_random(self):
		for i in range(10):
			ele = self.elist_100.random()
			ele2 = self.elist_100.random()
			self.assertIn(ele, self.elist_100)
			self.assertIn(ele2, self.elist_100)
			self.assertNotEqual(ele, ele2)

	def test_random_k(self):
		for i in range(10):
			ele = self.elist_100.random(k=10)
			self.assertEqual(len(ele), 10)

			for i in range(0, len(ele) - 1):
				e0 = ele[i]
				e1 = ele[i + 1]
				self.assertNotEqual(e0, e1)
				self.assertIn(e0, self.elist_100)
				self.assertIn(e1, self.elist_100)

	def test_path(self):
		val = 123
		entity: Elist = Elist([{'a': {'b': {'c': val}}}])
		self.assertEqual(entity.path(path='0/a/b/c', page=0, max_width=2), val)
		self.assertEqual(entity.path(path='0/a/b', page=0, max_width=2), {'c': val})
		self.assertEqual(entity.path(path='0/a', page=0, max_width=2), {'b': {'c': val}})

	def test_path_width_depth(self):
		entity: Elist = Elist([{'a': [i for i in range(100)]}])

		result = entity.path(path='0/a', page=0, max_width=10)
		self.assertEqual(result, [i for i in range(10)])
		result = entity.path(path='0/a', page=5, max_width=10)
		self.assertEqual(result, [i for i in range(50, 60)])

		result = entity.path(path='0/a', page=0, max_width=50)
		self.assertEqual(len(result), 50)

	def test_field(self):
		f = Elist.field()
		self.assertIsInstance(f, Field)
		self.assertIsInstance(f.default_factory, Callable)
		e = f.default_factory()
		self.assertIsInstance(e, Elist)
		self.assertEqual(len(e), 0)

		f = Elist.field(1, 2, 3)
		self.assertEqual(f.default_factory(), Elist([1, 2, 3]))


@dataclass
class FakeEntity(Entity):
	a: str
	b: str = 'b'
	c: elist = Elist.field(1, 2, 3)


class test_Entity(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.entity: FakeEntity = FakeEntity(a='a')

	def test_properties(self):
		self.assertTrue(self.entity.a, 'a')
		self.assertTrue(self.entity.b, 'b')
		self.assertTrue(self.entity.c, Elist([1, 2, 3]))
		self.assertEqual(len(self.entity._id), 22)
		self.assertEqual(self.entity._razred, 'FAKEENTITY')
		self.assertLessEqual(self.entity._ustvarjen, datetime.utcnow())
		self.assertLessEqual(self.entity._posodobljen, datetime.utcnow())
		self.assertIsInstance(self.entity._dnevnik, Elist)
		self.assertIsInstance(self.entity._povezave, Elist)
		self.assertEqual(len(self.entity.__dict__), 9)

	def test_povezi(self):
		entity = FakeEntity(a='a')
		entity1 = FakeEntity(a='b')
		self.assertEqual(len(entity._povezave), 0)
		entity.povezi(entity1)
		self.assertEqual(len(entity._povezave), 1)
		self.assertEqual(entity._povezave[0], entity1)


if __name__ == '__main__':
	unittest.main()
