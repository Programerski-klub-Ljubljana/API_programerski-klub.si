import unittest
from copy import deepcopy
from dataclasses import Field, dataclass
from datetime import datetime
from typing import Callable

from persistent.list import PersistentList

from core.domain._entity import Elist, Entity, Log, Elog, Edict
from core.domain._enums import LogLevel, LogType
from test.tutils import Entity_fixtures, EntityBig, EntitySmall


@dataclass
class E(Entity):
	value: int


class test_Elist(unittest.TestCase):
	def _assertEqualLogs(self, arr1, arr2):
		arr1 = deepcopy(arr1)
		arr2 = deepcopy(arr2)

		for l in arr1 + arr2:
			l.created = 'now'
		self.assertEqual(arr1, arr2)

	def _assertEqualLogsSize(self, size: int):
		self.assertEqual(len(self.elist._p_logs), size)
		self.assertEqual(len(self.elist.logs), size)
		self.assertEqual(self.elist.logs, self.elist._p_logs)

	@classmethod
	def setUpClass(cls) -> None:
		cls.elist_100 = Elist([E(value=i) for i in range(500)])

	def setUp(self):
		self.before = datetime.now()
		self.elist = Elist(data=Entity_fixtures.list(EntityBig, level=2))
		self.after = datetime.now()

		self.elist_empty = Elist()
		self.elist_int = Elist([i for i in range(3)])

	def test_init(self):
		self.assertIsInstance(self.elist, Elog)
		self.assertIsInstance(self.elist, Elist)

		self.assertEqual(self.elist._p_log, True)
		self.assertIsInstance(self.elist._p_logs, PersistentList)
		self.assertTrue(self.before < self.elist._p_created < self.after)
		self.assertTrue(self.before < self.elist._p_updated < self.after)

		self._assertEqualLogsSize(1)
		init_log = self.elist._p_logs[0]
		self.assertEqual(init_log.level, LogLevel.DEBUG)
		self.assertEqual(init_log.type, LogType.ELIST_INIT)
		self.assertTrue(self.before < init_log.created < self.after)

		self.assertEqual(init_log.kwargs, {})

		self.assertEqual(init_log.args, "this is fucked!")

		self.assertEqual(
			str(init_log.args)[-300:],
			"ta', 'e': None, 'f': None, 'g': None, 'h': None}, "
			"[3.21, False, 321, 'mata', None, None, None, None]]}), "
			"[3.21, False, 321, 'mata', None, None, None, None], "
			"{'a': True, 'b': 123, 'c': 1.23, 'd': 'data', 'e': None, 'f': None, 'g': None, 'h': None}, "
			"(3.21, False, 321, 'mata', None, None, None, None)))"
		)

		self.assertEqual(
			init_log.msg[:300],
			"__init__(3.21, False, 321, 'mata', "
			"EntityBig(a=True, b=32, c=0.23, d='asd', "
			"e=EntityBig(a=True, b=32, c=0.23, d='asd', e=None, f=None, g=None, h=None, "
			"j=EntitySmall(a=True, b=32, c=0.23, d='asd', "
			"e=EntitySmall(a=True, b=32, c=0.23, d='asd', "
			"e=EntitySmall(a=True, b=32, c=0.23, d='asd', e=None, f=None")

		self.assertEqual(
			init_log.msg[-300:],
			"ta', 'e': None, 'f': None, 'g': None, 'h': None}, "
			"[3.21, False, 321, 'mata', None, None, None, None]]}), "
			"[3.21, False, 321, 'mata', None, None, None, None], "
			"{'a': True, 'b': 123, 'c': 1.23, 'd': 'data', 'e': None, 'f': None, 'g': None, 'h': None}, "
			"(3.21, False, 321, 'mata', None, None, None, None)))")

	def test_log_type(self):
		self.assertEqual(self.elist.log_type, LogType.ELIST)

	def test_data(self):
		# * LEVEL 0
		self.assertEqual(self.elist[0], 3.21)
		self.assertEqual(self.elist[1], False)
		self.assertEqual(self.elist[2], 321)
		self.assertEqual(self.elist[3], 'mata')

		# * LEVEL 1: ENTITY
		self.assertIsInstance(self.elist[4], EntityBig)
		self.assertEqual(self.elist[4].a, True)
		self.assertEqual(self.elist[4].d, 'asd')
		# * LEVEL 2: -> ENTITY
		self.assertIsInstance(self.elist[4].e, EntityBig)
		self.assertEqual(self.elist[4].e.d, 'asd')
		# * LEVEL 2: -> ELIST
		self.assertIsInstance(self.elist[4].f, Elist)
		self.assertEqual(self.elist[4].f[2], 321)
		# * LEVEL 2: -> EDICT
		self.assertIsInstance(self.elist[4].g, Edict)
		self.assertEqual(self.elist[4].g['b'], 123)
		# * LEVEL 2: -> TUPLE
		self.assertIsInstance(self.elist[4].h, Elist)
		self.assertEqual(self.elist[4].f[0], 3.21)

		# * LEVEL 1: ELIST
		self.assertIsInstance(self.elist[5], Elist)
		self.assertEqual(self.elist[5][0], 3.21)
		self.assertEqual(self.elist[5][3], 'mata')
		# * LEVEL 2: -> ENTITY
		self.assertIsInstance(self.elist[5][4], EntityBig)
		self.assertEqual(self.elist[5][4].d, 'asd')
		# * LEVEL 2: -> ELIST
		self.assertIsInstance(self.elist[5][5], Elist)
		self.assertEqual(self.elist[5][5][2], 321)
		# * LEVEL 2: -> EDICT
		self.assertIsInstance(self.elist[5][6], Edict)
		self.assertEqual(self.elist[5][6]['b'], 123)
		# * LEVEL 2: -> TUPLE
		self.assertIsInstance(self.elist[5][7], Elist)
		self.assertEqual(self.elist[5][7][2], 321)

		# * LEVEL 1: EDICT
		self.assertIsInstance(self.elist[6], Edict)
		self.assertEqual(self.elist[6]['b'], 123)
		self.assertEqual(self.elist[6]['c'], 1.23)
		# * LEVEL 2: -> ENTITY
		self.assertIsInstance(self.elist[6]['e'], EntityBig)
		self.assertEqual(self.elist[6]['e'].d, 'asd')
		# * LEVEL 2: -> ELIST
		self.assertIsInstance(self.elist[6]['f'], Elist)
		self.assertEqual(self.elist[6]['f'][2], 321)
		# * LEVEL 2: -> EDICT
		self.assertIsInstance(self.elist[6]['g'], Edict)
		self.assertEqual(self.elist[6]['g']['b'], 123)
		# * LEVEL 2: -> TUPLE
		self.assertIsInstance(self.elist[6]['h'], Elist)
		self.assertEqual(self.elist[6]['h'][2], 321)

	def test_setitem(self):
		# * LEVEL 1 (SHOULD LOGS)
		self.elist[0] = 321
		self.elist[1] = EntitySmall(a=False, b=1234, c=1.234, d='new', e=None, f=None, g=None, h=None)
		self.elist[2] = [[1, 2, 3], {'a': 'a'}]

		self.assertEqual(self.elist[0], 321)
		self.assertEqual(self.elist[1].b, 1234)
		self.assertEqual(self.elist[2], [[1, 2, 3], {'a': 'a'}])

		# * IT SHOULD CONVERT INNER STRUCTURE TO RIGHT OBJECT
		self.assertIsInstance(self.elist[2], Elist)
		self.assertIsInstance(self.elist[2][0], Elist)
		self.assertIsInstance(self.elist[2][1], Edict)

		# * LEVEL 2 (SHOULD LOGS)
		self.elist[5][0] = 12.3
		self.elist[6]['b'] = 987

		self.assertEqual(self.elist[5][0], 12.3)
		self.assertEqual(self.elist[6]['b'], 987)

		# * LEVEL 3 (SHOULD NOT LOGS)
		self.elist[5][4].b = 983
		self.elist[5][5][3] = 'asdfasd'

		self.assertEqual(self.elist[5][4].b, 983)
		self.assertEqual(self.elist[5][5][3], 'asdfasd')

		self.assertEqual(len(self.elist._p_logs), 4)
		self.assertEqual(len(self.elist.logs), 6)

		all_logs = [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__setitem__(i=0, item=321)', created='now', args=(), kwargs={'i': 0, 'item': 321}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST,
				msg="__setitem__(i=1, item=EntitySmall(a=False, b=1234, c=1.234, d='new', e=None, f=None, g=None, h=None))", created='now', args=(),
				kwargs={'i': 1, 'item': EntitySmall(a=False, b=1234, c=1.234, d='new', e=None, f=None, g=None, h=None)}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST, msg="__setitem__(i=2, item=[[1, 2, 3], {'a': 'a'}])", created='now', args=(),
				kwargs={'item': [[1, 2, 3], {'a': 'a'}], 'i': 2}),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="[5].__setitem__(i=0, item=12.3)", args=(), kwargs={'i': 0, 'item': 12.3}),
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="[6].__setitem__(key='b', item=987)", args=(), kwargs={'key': 'b', 'item': 987})
		]

		self._assertEqualLogs(self.elist._p_logs[1:], all_logs[:3])
		self._assertEqualLogs(self.elist.logs[1:], all_logs)

	def test_add(self):
		self.elist_int = self.elist_int + [[1], {'a': 'a'}]

		self.assertEqual(self.elist_int._p_logs, self.elist_int.logs)
		self.assertIsInstance(self.elist_int, Elist)
		self.assertIsInstance(self.elist_int[-1], Edict)
		self.assertIsInstance(self.elist_int[-2], Elist)

		self.assertEqual(self.elist_int, [0, 1, 2, [1], {'a': 'a'}])

		self._assertEqualLogs(self.elist_int._p_logs, self.elist_int.logs)
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST_INIT,
				msg='__init__(0, 1, 2)', created='now', args=(0, 1, 2), kwargs={}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST,
				msg="__add__(other=[[1], {'a': 'a'}])", created='now', args=(), kwargs={'other': [[1], {'a': 'a'}]})
		])

	def test_radd(self):
		self.elist_int = [[1], {'a': 'a'}] + self.elist_int

		self.assertEqual(self.elist_int._p_logs, self.elist_int.logs)
		self.assertIsInstance(self.elist_int, Elist)
		self.assertIsInstance(self.elist_int[1], Edict)
		self.assertIsInstance(self.elist_int[0], Elist)

		self.assertEqual(self.elist_int, [[1], {'a': 'a'}, 0, 1, 2])

		self._assertEqualLogs(self.elist_int._p_logs, self.elist_int.logs)
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST_INIT, msg='__init__(0, 1, 2)', created='now', args=(0, 1, 2), kwargs={}),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="__radd__(other=[[1], {'a': 'a'}])", created='now', args=(),
			    kwargs={'other': [[1], {'a': 'a'}]})
		])

	def test_iadd(self):
		self.elist_int += [[1], {'a': 'a'}]

		self.assertEqual(self.elist_int._p_logs, self.elist_int.logs)
		self.assertIsInstance(self.elist_int, Elist)
		self.assertIsInstance(self.elist_int[-1], Edict)
		self.assertIsInstance(self.elist_int[-2], Elist)

		self.assertEqual(self.elist_int, [0, 1, 2, [1], {'a': 'a'}])

		self._assertEqualLogs(self.elist_int._p_logs, self.elist_int.logs)
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST_INIT,
				msg='__init__(0, 1, 2)', created='now', args=(0, 1, 2), kwargs={}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST,
				msg="__iadd__(other=[[1], {'a': 'a'}])", created='now', args=(), kwargs={'other': [[1], {'a': 'a'}]})
		])

	def test_mul(self):
		self.elist_int += [[1], {'a': 'a'}]
		self.elist_int = self.elist_int * 2

		self.assertEqual(self.elist_int._p_logs, self.elist_int.logs)
		self.assertIsInstance(self.elist_int, Elist)
		self.assertIsInstance(self.elist_int[3], Elist)
		self.assertIsInstance(self.elist_int[4], Edict)
		self.assertIsInstance(self.elist_int[-2], Elist)
		self.assertIsInstance(self.elist_int[-1], Edict)

		self.assertEqual(self.elist_int, [0, 1, 2, [1], {'a': 'a'}, 0, 1, 2, [1], {'a': 'a'}])

		self._assertEqualLogs(self.elist_int._p_logs, self.elist_int.logs)
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST_INIT,
				msg='__init__(0, 1, 2)', created='now', args=(0, 1, 2), kwargs={}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST,
				msg="__iadd__(other=[[1], {'a': 'a'}])", created='now', args=(), kwargs={'other': [[1], {'a': 'a'}]}),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__mul__(n=2)', created='now', args=(), kwargs={'n': 2})
		])

	def test_rmul(self):
		self.elist_int += [[1], {'a': 'a'}]
		self.elist_int = 2 * self.elist_int

		self.assertEqual(self.elist_int._p_logs, self.elist_int.logs)
		self.assertIsInstance(self.elist_int, Elist)
		self.assertIsInstance(self.elist_int[3], Elist)
		self.assertIsInstance(self.elist_int[4], Edict)
		self.assertIsInstance(self.elist_int[-2], Elist)
		self.assertIsInstance(self.elist_int[-1], Edict)

		self.assertEqual(self.elist_int, [0, 1, 2, [1], {'a': 'a'}, 0, 1, 2, [1], {'a': 'a'}])

		self._assertEqualLogs(self.elist_int._p_logs, self.elist_int.logs)
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST_INIT,
				msg='__init__(0, 1, 2)', created='now', args=(0, 1, 2), kwargs={}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST,
				msg="__iadd__(other=[[1], {'a': 'a'}])", created='now', args=(), kwargs={'other': [[1], {'a': 'a'}]}),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__rmul__(n=2)', created='now', args=(), kwargs={'n': 2})
		])

	def test_imul(self):
		self.elist_int += [[1], {'a': 'a'}]
		self.elist_int *= 2

		self.assertEqual(self.elist_int._p_logs, self.elist_int.logs)
		self.assertIsInstance(self.elist_int, Elist)
		self.assertIsInstance(self.elist_int[3], Elist)
		self.assertIsInstance(self.elist_int[4], Edict)
		self.assertIsInstance(self.elist_int[-2], Elist)
		self.assertIsInstance(self.elist_int[-1], Edict)

		self.assertEqual(self.elist_int, [0, 1, 2, [1], {'a': 'a'}, 0, 1, 2, [1], {'a': 'a'}])

		self._assertEqualLogs(self.elist_int._p_logs, self.elist_int.logs)
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST_INIT,
				msg='__init__(0, 1, 2)', created='now', args=(0, 1, 2), kwargs={}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST,
				msg="__iadd__(other=[[1], {'a': 'a'}])", created='now', args=(), kwargs={'other': [[1], {'a': 'a'}]}),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__imul__(n=2)', created='now', args=(), kwargs={'n': 2})
		])

	def test_contains(self):
		self.assertTrue(1 not in self.elist_empty)
		self.assertTrue(None not in self.elist_empty)
		self.assertTrue(1 in self.elist_int)
		self.assertTrue(-1 not in self.elist_int)

	def test_append(self):
		self.elist_int.append([[1], {'a': 'a'}])

		self.assertEqual(self.elist_int._p_logs, self.elist_int.logs)
		self.assertIsInstance(self.elist_int, Elist)
		self.assertIsInstance(self.elist_int[-1], Elist)
		self.assertIsInstance(self.elist_int[-1][0], Elist)
		self.assertIsInstance(self.elist_int[-1][1], Edict)

		self.assertEqual(self.elist_int, [0, 1, 2, [[1], {'a': 'a'}]])

		self._assertEqualLogs(self.elist_int._p_logs, self.elist_int.logs)
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST_INIT,
				msg='__init__(0, 1, 2)', created='now', args=(0, 1, 2), kwargs={}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST, msg="append(item=[[1], {'a': 'a'}])", created='now', args=(),
				kwargs={'item': [[1], {'a': 'a'}]})
		])

	def test_clear(self):
		self.elist_int.clear()
		self.assertEqual(self.elist_int, [])
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST_INIT, msg='__init__(0, 1, 2)', created='now', args=(0, 1, 2), kwargs={}),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='clear()', created='now', args=(), kwargs={})
		])

	def test_insert(self):
		self.elist_int.insert(1, [[1], {'a': 'a'}])

		self.assertEqual(self.elist_int._p_logs, self.elist_int.logs)
		self.assertIsInstance(self.elist_int, Elist)
		self.assertIsInstance(self.elist_int[1], Elist)
		self.assertIsInstance(self.elist_int[1][0], Elist)
		self.assertIsInstance(self.elist_int[1][1], Edict)

		self.assertEqual(self.elist_int, [0, [[1], {'a': 'a'}], 1, 2])

		self._assertEqualLogs(self.elist_int._p_logs, self.elist_int.logs)
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST_INIT,
				msg='__init__(0, 1, 2)', created='now', args=(0, 1, 2), kwargs={}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST, msg="insert(i=1, item=[[1], {'a': 'a'}])", created='now', args=(),
				kwargs={'i': 1, 'item': [[1], {'a': 'a'}]})
		])

	def test_pop(self):
		self.assertEqual(self.elist_int.pop(1), 1)
		self.assertEqual(self.elist_int, [0, 2])
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST_INIT, args=(0, 1, 2), kwargs={}, msg='__init__(0, 1, 2)'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, args=(), kwargs={'i': 1}, msg='pop(i=1)')])

	def test_remove(self):
		self.elist_int.remove(1)
		self.assertEqual(self.elist_int, [0, 2])
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST_INIT, args=(0, 1, 2), kwargs={}, msg='__init__(0, 1, 2)'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, args=(), kwargs={'item': 1}, msg='remove(item=1)')])

	def test_reverse(self):
		self.elist_int.reverse()
		self.assertEqual(self.elist_int, [2, 1, 0])
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(level=LogLevel.DEBUG, kwargs={}, args=(0, 1, 2), type=LogType.ELIST_INIT, msg='__init__(0, 1, 2)'),
			Log(level=LogLevel.DEBUG, kwargs={}, args=(), type=LogType.ELIST, msg='reverse()')])

	def test_sort(self):
		self.elist_int.sort(key=lambda e: e, reverse=True)
		self.assertEqual(self.elist_int, [2, 1, 0])
		self.elist_int.sort(key=lambda e: e, reverse=False)
		self.assertEqual(self.elist_int, [0, 1, 2])
		self.elist_int.sort()
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST_INIT,
				msg='__init__(0, 1, 2)', created='now', args=(0, 1, 2), kwargs={}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST,
				msg="sort(reverse=True, key='lambda e: e')", created='now', args=(), kwargs={'key': 'lambda e: e', 'reverse': True}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST,
				msg="sort(reverse=False, key='lambda e: e')", created='now', args=(), kwargs={'key': 'lambda e: e', 'reverse': False}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST,
				msg='sort(reverse=False, key=None)', created='now', args=(), kwargs={'key': None, 'reverse': False})
		])

	def test_extend(self):
		self.elist_int.extend([[1], {'a': 'a'}])

		self.assertEqual(self.elist_int._p_logs, self.elist_int.logs)
		self.assertIsInstance(self.elist_int, Elist)
		self.assertIsInstance(self.elist_int[-2], Elist)
		self.assertIsInstance(self.elist_int[-1], Edict)

		self.assertEqual(self.elist_int, [0, 1, 2, [1], {'a': 'a'}])

		self._assertEqualLogs(self.elist_int._p_logs, self.elist_int.logs)
		self._assertEqualLogs(self.elist_int._p_logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST_INIT,
				msg='__init__(0, 1, 2)', created='now', args=(0, 1, 2), kwargs={}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST,
				msg="extend(other=[[1], {'a': 'a'}])", created='now', args=(), kwargs={'other': [[1], {'a': 'a'}]})
		])

	def test_random(self):
		for i in range(3):
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

		ele = entity.path(path='0/a/b', page=0, max_width=2)
		self.assertIsInstance(ele, Edict)
		self.assertEqual(ele, {'c': val})

		ele = entity.path(path='0/a', page=0, max_width=2)
		self.assertIsInstance(ele, Edict)
		self.assertEqual(ele, {'b': {'c': val}})

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
