import unittest
from dataclasses import Field, dataclass
from datetime import datetime
from typing import Callable

import shortuuid

from core.domain._entity import Elist, Entity, elist, Log
from core.domain._enums import LogLevel, LogTheme


@dataclass
class E(Entity):
	value: int


class test_Elist(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.elist_100 = Elist([E(value=i) for i in range(10000)])

	def setUp(self):
		self.elist = Elist([E(value=i) for i in range(6)])
		self.elist_empty = Elist([])
		self.elist_int = Elist([i for i in range(3)])

	def test_log_call(self):
		self.elist_int._log_call(self.test_log_call, kwargs={'arg0': 'arg0', 'arg1': '123'})
		self.assertEqual(self.elist_int._logs, [Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='test_log_call(arg0="arg0", arg1="123")')])
		print(self.elist_int)

	def test_setitem(self):
		self.elist_int[1] = 10
		self.assertEqual(self.elist_int, [0, 10, 2])
		self.assertEqual(self.elist_int._logs, [Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='__setitem__(i=1, item=10)')])
		print(self.elist_int)

	def test_add(self):
		self.elist_int = self.elist_int + Elist([3, 4])
		self.assertEqual(self.elist_int, [0, 1, 2, 3, 4])
		self.assertEqual(self.elist_int._logs, [Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='__add__(other=[3, 4])')])
		print(self.elist_int)

	def test_radd(self):
		self.elist_int = [-2, -1] + self.elist_int
		self.assertEqual(self.elist_int, [-2, -1, 0, 1, 2])
		self.assertEqual(self.elist_int._logs, [Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='__radd__(other=[-2, -1])')])
		print(self.elist_int)

	def test_iadd(self):
		self.elist_int += [3, 4]
		self.assertEqual(self.elist_int, [0, 1, 2, 3, 4])
		self.assertEqual(self.elist_int._logs, [Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='__iadd__(other=[3, 4])')])
		print(self.elist_int)

	def test_mul(self):
		self.elist_int = self.elist_int * 3
		self.assertEqual(self.elist_int, [0, 1, 2, 0, 1, 2, 0, 1, 2])
		self.assertEqual(self.elist_int._logs, [Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='__mul__(other=3)')])
		print(self.elist_int)

	def test_rmul(self):
		self.elist_int = 3 * self.elist_int
		self.assertEqual(self.elist_int, [0, 1, 2, 0, 1, 2, 0, 1, 2])
		self.assertEqual(self.elist_int._logs, [Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='__rmul__(other=3)')])
		print(self.elist_int)

	def test_imul(self):
		self.elist_int *= 3
		self.assertEqual(self.elist_int, [0, 1, 2, 0, 1, 2, 0, 1, 2])
		self.assertEqual(self.elist_int._logs, [Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='__imul__(other=3)')])
		print(self.elist_int)

	def test_contains(self):
		self.assertTrue(1 not in self.elist_empty)
		self.assertTrue(None not in self.elist_empty)
		for i in range(10):
			if i <= 5:
				self.assertTrue(E(value=i) in self.elist)
			else:
				self.assertTrue(E(value=i) not in self.elist)

	def test_append_pop(self):
		self.elist_empty.append(123)
		self.assertEqual(self.elist_empty[-1], 123)

		self.elist_empty.pop(0)
		self.assertEqual(len(self.elist_empty), 0)

		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='test_log_call(arg0="arg", arg1=123, arg2="arg2")')
		])

	def test_clear(self):
		self.elist_int.clear()
		self.assertEqual(self.elist_int, [])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='clear()')
		])

	def test_insert(self):
		self.elist_int.insert(1, 123)
		self.assertEqual(self.elist_int, [0, 123, 1, 2])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='insert(i=1, item=123)')
		])

	def test_pop(self):
		self.elist_int.pop(1)
		self.assertEqual(self.elist_int, [0, 2])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='pop(i=1)')
		])

	def test_remove(self):
		self.elist_int.remove(1)
		self.assertEqual(self.elist_int, [0, 2])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='remove(item=1)')
		])

	def test_reverse(self):
		self.elist_int.reverse()
		self.assertEqual(self.elist_int, [2, 1, 0])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='reverse()')
		])

	def test_sort(self):
		self.elist_int.sort(key=lambda e: e, reverse=True)
		self.assertEqual(self.elist_int, [2, 1, 0])
		self.elist_int.sort(key=lambda e: e, reverse=False)
		self.assertEqual(self.elist_int, [0, 1, 2])

		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='test_log_call(arg0="arg", arg1=123, arg2="arg2")')
		])

	def test_extend(self):
		self.elist_int.extend([2, 1, 0])
		self.assertEqual(self.elist_int, [0, 1, 2, 2, 1, 0])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='extend(other=[2, 1, 0])')
		])

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
	def setUp(self) -> None:
		self.before = datetime.now()
		self.entity: FakeEntity = FakeEntity(a='a')
		self.after = datetime.now()

	def test_attr(self):
		self.assertTrue(self.entity.a, 'a')
		self.assertTrue(self.entity.b, 'b')
		self.assertTrue(self.entity.c, Elist([1, 2, 3]))

		self.assertEqual(len(self.entity._id), len(shortuuid.uuid()))
		self.assertEqual(self.entity._type, "fakeentity")
		self.assertTrue(self.before < self.entity._created < self.after)
		self.assertTrue(self.before < self.entity._updated < self.after)

		self.assertIsInstance(self.entity._connections, Elist)
		self.assertEqual(self.entity._connections, [])

		self.assertIsInstance(self.entity._logs, Elist)
		self.assertEqual(self.entity._logs, [])

		self.assertEqual(len(self.entity.__dict__), 9)

	def test_setattr(self):
		self.assertEqual(self.entity.a, 'a')
		self.assertEqual(self.entity._logs, [])

		self.entity.a = 'b'
		self.assertEqual(self.entity.a, 'b')
		self.assertEqual(self.entity._logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='a = "b"'),
		])

		setattr(self.entity, 'a', 10)
		self.assertEqual(self.entity.a, 10)
		self.assertEqual(self.entity._logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='a = "b"'),
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='a = 10')
		])

	def test_delattr(self):
		with self.assertRaises(Exception):
			del self.entity.a
		with self.assertRaises(Exception):
			delattr(self.entity, 'a')

	def test_logs(self):
		self.entity.a = 'b'
		self.entity.c.append(4)
		self.entity.c.append('4')
		self.entity.c.remove('4')
		self.assertEqual(self.entity._logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='a = "b"')
		])

	def test_logs_property(self):
		self.assertEqual(self.entity.logs, [])
		self.entity.a = 'new a'
		self.entity.c.append('new c')
		self.entity.b = 'new b'
		self.entity.c.append(123)
		logs = self.entity.logs
		self.assertEqual(logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='a = "new a"'),
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='c.append("new c")'),
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='b = "new b"'),
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='c.append(123)')
		])

		for i in range(len(logs) - 1):
			self.assertGreater(logs[i + 1]._created, logs[i]._created)

	def test_log_call(self):
		self.assertEqual(self.entity._logs, [])
		self.entity.log_call(self.test_log_call, {'kwarg0': 'kwarg0', 'kwarg1': 123})
		self.assertEqual(self.entity._logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg='test_log_call(kwarg0="kwarg0", kwarg1=123)')
		])

	def test_equal(self):
		equal_entity = FakeEntity('a')
		not_equal_entity = FakeEntity('b')
		self.assertEqual(self.entity, equal_entity)
		self.assertNotEqual(self.entity, not_equal_entity)

		self.assertTrue(self.entity.equal(self.entity))
		self.assertTrue(self.entity.equal(equal_entity))
		self.assertFalse(self.entity.equal(not_equal_entity))

	def test_connect(self):
		entity = FakeEntity(a='a')
		entity1 = FakeEntity(a='b')

		self.assertEqual(len(entity._connections), 0)
		self.assertEqual(len(entity1._connections), 0)

		entity.connect(entity1)

		self.assertEqual(len(entity._connections), 1)
		self.assertEqual(entity._connections[0], entity1)

		self.assertEqual(len(entity1._connections), 1)
		self.assertEqual(entity1._connections[0], entity)

		self.assertEqual(entity.logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg="_connections.append(FakeEntity(a='b', b='b', c=[1, 2, 3]))")])
		self.assertEqual(entity1.logs, [
			Log(level=LogLevel.DEBUG, theme=LogTheme.SPREMEMBA, msg="_connections.append(FakeEntity(a='a', b='b', c=[1, 2, 3]))")])


if __name__ == '__main__':
	unittest.main()
