import unittest
from dataclasses import Field, dataclass
from typing import Callable

from core.domain._entity import Elist, Entity, Log
from core.domain._enums import LogLevel, LogType


@dataclass
class E(Entity):
	value: int


class test_Elist(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cls.elist_100 = Elist([E(value=i) for i in range(500)])

	def setUp(self):
		self.elist = Elist([E(value=i) for i in range(6)])
		self.elist_empty = Elist()
		self.elist_int = Elist([i for i in range(3)])

	def test_log_call(self):
		self.elist_int._log_call(self.test_log_call, arg0='arg0', arg1='123')
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="test_log_call(arg0='arg0', arg1='123')")])

	def test_setitem(self):
		self.elist_int[1] = 10
		self.elist_int[2] = "10"
		self.assertEqual(self.elist_int, [0, 10, "10"])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__setitem__(i=1, item=10)'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="__setitem__(i=2, item='10')")
		])

	def test_add(self):
		self.elist_int = self.elist_int + Elist([3, 4])
		self.elist_int = self.elist_int + Elist([5, 6])
		self.assertEqual(self.elist_int, [0, 1, 2, 3, 4, 5, 6])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__add__(other=[3, 4])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__add__(other=[5, 6])')
		])

	def test_radd(self):
		self.elist_int = [-2, -1] + self.elist_int
		self.elist_int = [-4, -3] + self.elist_int
		self.assertEqual(self.elist_int, [-4, -3, -2, -1, 0, 1, 2])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__radd__(other=[-2, -1])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__radd__(other=[-4, -3])')
		])

	def test_iadd(self):
		self.elist_int += [3, 4]
		self.elist_int += [5, 6]
		self.assertEqual(self.elist_int, [0, 1, 2, 3, 4, 5, 6])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__iadd__(other=[3, 4])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__iadd__(other=[5, 6])')
		])

	def test_mul(self):
		self.elist_int = self.elist_int * 2
		self.elist_int = self.elist_int * 2
		self.assertEqual(self.elist_int, [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__mul__(n=2)'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__mul__(n=2)')
		])

	def test_rmul(self):
		self.elist_int = 2 * self.elist_int
		self.elist_int = 2 * self.elist_int
		self.assertEqual(self.elist_int, [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__rmul__(n=2)'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__rmul__(n=2)')
		])

	def test_imul(self):
		self.elist_int *= 2
		self.elist_int *= 2
		self.assertEqual(self.elist_int, [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__imul__(n=2)'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__imul__(n=2)')
		])

	def test_contains(self):
		self.assertTrue(1 not in self.elist_empty)
		self.assertTrue(None not in self.elist_empty)
		for i in range(10):
			if i <= 5:
				self.assertTrue(E(value=i) in self.elist)
			else:
				self.assertTrue(E(value=i) not in self.elist)

	def test_append(self):
		self.elist_int.append(123)
		self.assertEqual(self.elist_int, [0, 1, 2, 123])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='append(item=123)')])

	def test_clear(self):
		self.elist_int.clear()
		self.assertEqual(self.elist_int, [])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='clear()')])

	def test_insert(self):
		self.elist_int.insert(1, 123)
		self.assertEqual(self.elist_int, [0, 123, 1, 2])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='insert(i=1, item=123)')])

	def test_pop(self):
		self.elist_int.pop(1)
		self.assertEqual(self.elist_int, [0, 2])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='pop(i=1)')])

	def test_remove(self):
		self.elist_int.remove(1)
		self.assertEqual(self.elist_int, [0, 2])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='remove(item=1)')])

	def test_reverse(self):
		self.elist_int.reverse()
		self.assertEqual(self.elist_int, [2, 1, 0])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='reverse()')])

	def test_sort(self):
		self.elist_int.sort(key=lambda e: e, reverse=True)
		self.assertEqual(self.elist_int, [2, 1, 0])
		self.elist_int.sort(key=lambda e: e, reverse=False)
		self.assertEqual(self.elist_int, [0, 1, 2])
		self.elist_int.sort()
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='sort(reverse=True, key=lambda e: e)'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='sort(reverse=False, key=lambda e: e)'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='sort(reverse=False, key=None)')
		])

	def test_extend(self):
		self.elist_int.extend([2, 1, 0])
		self.assertEqual(self.elist_int, [0, 1, 2, 2, 1, 0])
		self.assertEqual(self.elist_int._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(args=[0, 1, 2])'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='extend(other=[2, 1, 0])')])

	def test_random(self):
		for i in range(10):
			ele = self.elist_100.random()
			ele2 = self.elist_100.random()
			self.assertIn(ele, self.elist_100)
			self.assertIn(ele2, self.elist_100)
			self.assertNotEqual(ele, ele2)

	def test_random_k(self):
		for i in range(5):
			ele = self.elist_100.random(k=3)
			self.assertEqual(len(ele), 3)

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

		f = Elist.field(data=[1, 2, 3])
		self.assertEqual(f.default_factory(), Elist([1, 2, 3]))


if __name__ == '__main__':
	unittest.main()
