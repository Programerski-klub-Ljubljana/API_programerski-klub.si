import unittest
from copy import deepcopy
from datetime import datetime

from persistent.list import PersistentList

from core.domain._entity import Edict, Elist, Elog, Log
from core.domain._enums import LogType, LogLevel
from test.tutils import Entity_fixtures, EntityBig, EntitySmall


class test_Edict(unittest.TestCase):
	def _assertEqualLogs(self, arr1, arr2):
		arr1 = deepcopy(arr1)
		arr2 = deepcopy(arr2)

		for l in arr1 + arr2:
			l.created = 'now'
		self.assertEqual(arr1, arr2)

	def _assertEqualLogsSize(self, size: int):
		self.assertEqual(len(self.edict._p_logs), size)
		self.assertEqual(len(self.edict.logs), size)
		self.assertEqual(self.edict.logs, self.edict._p_logs)

	def setUp(self) -> None:
		self.before = datetime.now()
		self.edict = Edict(data=Entity_fixtures.dict(EntityBig, level=2))
		self.after = datetime.now()

	def test_init(self):
		self.assertIsInstance(self.edict, Elog)
		self.assertIsInstance(self.edict, Edict)

		self.assertEqual(self.edict._p_log, True)
		self.assertIsInstance(self.edict._p_logs, PersistentList)
		self.assertTrue(self.before < self.edict._p_created < self.after)
		self.assertTrue(self.before < self.edict._p_updated < self.after)

		self._assertEqualLogsSize(1)
		init_log = self.edict._p_logs[0]
		self.assertEqual(init_log.level, LogLevel.DEBUG)
		self.assertEqual(init_log.type, LogType.EDICT_INIT)
		self.assertTrue(self.before < init_log.created < self.after)
		self.assertEqual(init_log.args, tuple())

		self.assertEqual(
			str(init_log.kwargs)[:300],
			"{'a': True, 'b': 123, 'c': 1.23, 'd': 'data', "
			"'e': EntityBig(a=True, b=32, c=0.23, d='asd', "
			"e=EntityBig(a=True, b=32, c=0.23, d='asd', e=None, f=None, g=None, h=None, "
			"j=EntitySmall(a=True, b=32, c=0.23, d='asd', "
			"e=EntitySmall(a=True, b=32, c=0.23, d='asd', "
			"e=EntitySmall(a=True, b=32, c=0.23, d='asd'")

		self.assertEqual(
			str(init_log.kwargs)[-300:],
			"ta', 'e': None, 'f': None, 'g': None, 'h': None}, "
			"[3.21, False, 321, 'mata', None, None, None, None]]}), "
			"[3.21, False, 321, 'mata', None, None, None, None], "
			"{'a': True, 'b': 123, 'c': 1.23, 'd': 'data', 'e': None, 'f': None, 'g': None, 'h': None}, "
			"(3.21, False, 321, 'mata', None, None, None, None))}")

		self.assertEqual(
			init_log.msg[:300],
			"__init__(a=True, b=123, c=1.23, d='data', "
			"e=EntityBig(a=True, b=32, c=0.23, d='asd', "
			"e=EntityBig(a=True, b=32, c=0.23, d='asd', e=None, f=None, g=None, h=None, "
			"j=EntitySmall(a=True, b=32, c=0.23, d='asd', "
			"e=EntitySmall(a=True, b=32, c=0.23, d='asd', "
			"e=EntitySmall(a=True, b=32, c=0.23, d='asd', e=Non")

		self.assertEqual(
			init_log.msg[-300:],
			"ta', 'e': None, 'f': None, 'g': None, 'h': None}, "
			"[3.21, False, 321, 'mata', None, None, None, None]]}), "
			"[3.21, False, 321, 'mata', None, None, None, None], "
			"{'a': True, 'b': 123, 'c': 1.23, 'd': 'data', 'e': None, 'f': None, 'g': None, 'h': None}, "
			"(3.21, False, 321, 'mata', None, None, None, None)))")

	def test_log_type(self):
		self.assertEqual(self.edict.log_type, LogType.EDICT)

	def test_data(self):
		# * LEVEL 0
		self.assertEqual(self.edict['a'], True)
		self.assertEqual(self.edict['b'], 123)
		self.assertEqual(self.edict['c'], 1.23)
		self.assertEqual(self.edict['d'], 'data')

		# * LEVEL 1: ENTITY
		self.assertIsInstance(self.edict['e'], EntityBig)
		self.assertEqual(self.edict['e'].a, True)
		self.assertEqual(self.edict['e'].d, 'asd')
		# * LEVEL 2: -> ENTITY
		self.assertIsInstance(self.edict['e'].e, EntityBig)
		self.assertEqual(self.edict['e'].e.d, 'asd')
		# * LEVEL 2: -> ELIST
		self.assertIsInstance(self.edict['e'].f, Elist)
		self.assertEqual(self.edict['e'].f[2], 321)
		# * LEVEL 2: -> EDICT
		self.assertIsInstance(self.edict['e'].g, Edict)
		self.assertEqual(self.edict['e'].g['b'], 123)
		# * LEVEL 2: -> TUPLE
		self.assertIsInstance(self.edict['e'].h, Elist)
		self.assertEqual(self.edict['e'].f[0], 3.21)

		# * LEVEL 1: ELIST
		self.assertIsInstance(self.edict['f'], Elist)
		self.assertEqual(self.edict['f'][0], 3.21)
		self.assertEqual(self.edict['f'][3], 'mata')
		# * LEVEL 2: -> ENTITY
		self.assertIsInstance(self.edict['f'][4], EntityBig)
		self.assertEqual(self.edict['f'][4].d, 'asd')
		# * LEVEL 2: -> ELIST
		self.assertIsInstance(self.edict['f'][5], Elist)
		self.assertEqual(self.edict['f'][5][2], 321)
		# * LEVEL 2: -> EDICT
		self.assertIsInstance(self.edict['f'][6], Edict)
		self.assertEqual(self.edict['f'][6]['b'], 123)
		# * LEVEL 2: -> TUPLE
		self.assertIsInstance(self.edict['f'][7], Elist)
		self.assertEqual(self.edict['f'][7][2], 321)

		# * LEVEL 1: EDICT
		self.assertIsInstance(self.edict['g'], Edict)
		self.assertEqual(self.edict['g']['b'], 123)
		self.assertEqual(self.edict['g']['c'], 1.23)
		# * LEVEL 2: -> ENTITY
		self.assertIsInstance(self.edict['g']['e'], EntityBig)
		self.assertEqual(self.edict['g']['e'].d, 'asd')
		# * LEVEL 2: -> ELIST
		self.assertIsInstance(self.edict['g']['f'], Elist)
		self.assertEqual(self.edict['g']['f'][2], 321)
		# * LEVEL 2: -> EDICT
		self.assertIsInstance(self.edict['g']['g'], Edict)
		self.assertEqual(self.edict['g']['g']['b'], 123)
		# * LEVEL 2: -> TUPLE
		self.assertIsInstance(self.edict['g']['h'], Elist)
		self.assertEqual(self.edict['g']['h'][2], 321)

	def test_setitem(self):
		# * LEVEL 1 (SHOULD LOGS)
		self.edict['b'] = 321
		self.edict['e'] = EntitySmall(a=False, b=1234, c=1.234, d='new', e=None, f=None, g=None, h=None)
		self.edict['c'] = [[1, 2, 3], {'a': 'a'}]

		self.assertEqual(self.edict['b'], 321)
		self.assertEqual(self.edict['e'].b, 1234)
		self.assertEqual(self.edict['c'], [[1, 2, 3], {'a': 'a'}])

		# * IT SHOULD CONVERT INNER STRUCTURE TO RIGHT OBJECT
		self.assertIsInstance(self.edict['c'], Elist)
		self.assertIsInstance(self.edict['c'][0], Elist)
		self.assertIsInstance(self.edict['c'][1], Edict)

		# * LEVEL 2 (SHOULD LOGS)
		self.edict['f'][0] = 12.3
		self.edict['g']['b'] = 987

		self.assertEqual(self.edict['f'][0], 12.3)
		self.assertEqual(self.edict['g']['b'], 987)

		# * LEVEL 3 (SHOULD NOT LOGS)
		self.edict['h'][4].b = 983
		self.edict['h'][5][3] = 'asdfasd'

		self.assertEqual(self.edict['h'][4].b, 983)
		self.assertEqual(self.edict['h'][5][3], 'asdfasd')

		self.assertEqual(len(self.edict._p_logs), 4)
		self.assertEqual(len(self.edict.logs), 6)

		all_logs = [
			Log(
				level=LogLevel.DEBUG, type=LogType.EDICT, args=(),
				msg="__setitem__(key='b', item=321)", kwargs={'key': 'b', 'item': 321}),
			Log(
				level=LogLevel.DEBUG, type=LogType.EDICT, args=(),
				msg="__setitem__(key='e', item=EntitySmall(a=False, b=1234, c=1.234, d='new', e=None, f=None, g=None, h=None))",
				kwargs={'item': EntitySmall(a=False, b=1234, c=1.234, d='new', e=None, f=None, g=None, h=None), 'key': 'e'}),
			Log(
				level=LogLevel.DEBUG, type=LogType.EDICT, msg="__setitem__(key='c', item=[[1, 2, 3], {'a': 'a'}])", created='now', args=(),
				kwargs={'item': [[1, 2, 3], {'a': 'a'}], 'key': 'c'}),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="['f'].__setitem__(i=0, item=12.3)", args=(), kwargs={'i': 0, 'item': 12.3}),
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="['g'].__setitem__(key='b', item=987)", args=(), kwargs={'key': 'b', 'item': 987}),
		]

		self._assertEqualLogs(self.edict._p_logs[1:], all_logs[:3])
		self._assertEqualLogs(self.edict.logs[1:], all_logs)

	def test_delitem(self):
		self.assertTrue('b' in self.edict)
		self.assertTrue('e' in self.edict)

		del self.edict['b']
		del self.edict['e']

		self.assertTrue('b' not in self.edict)
		self.assertTrue('e' not in self.edict)

		self._assertEqualLogsSize(3)

		self._assertEqualLogs(self.edict.logs[1:], [
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__delitem__(key='b')", args=(), kwargs={'key': 'b'}),
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__delitem__(key='e')", args=(), kwargs={'key': 'e'}),
		])

	def test_clear(self):
		self.assertGreater(len(self.edict.data), 3)
		self.edict.clear()
		self.assertEqual(self.edict, {})

		self._assertEqualLogsSize(2)

		self._assertEqualLogs(self.edict._p_logs[1:], [Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="clear()", args=(), kwargs={})])

	def test_update(self):
		self.assertTrue('x' not in self.edict)
		self.assertTrue('d' in self.edict)
		self.assertEqual(self.edict['d'], 'data')
		self.edict.update(x='4', d=5)
		self.assertEqual(self.edict['x'], '4')
		self.assertEqual(self.edict['d'], 5)

		self._assertEqualLogsSize(3)

		self._assertEqualLogs(self.edict._p_logs[1:], [
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__setitem__(key='x', item='4')", args=(), kwargs={'key': 'x', 'item': '4'}),
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__setitem__(key='d', item=5)", args=(), kwargs={'key': 'd', 'item': 5})
		])

	def test_setdefault(self):
		self.assertEqual(self.edict['a'], True)

		self.assertEqual(self.edict.setdefault('a', 'value'), True)
		self.assertEqual('value', self.edict.setdefault('x', 'value'))

		self.assertEqual(self.edict['a'], True)
		self.assertEqual(self.edict['x'], 'value')

		self._assertEqualLogsSize(2)

		self._assertEqualLogs(self.edict._p_logs[1:], [
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__setitem__(key='x', item='value')", args=(), kwargs={'key': 'x', 'item': 'value'})
		])

	def test_pop(self):
		self.assertEqual(self.edict['b'], 123)
		self.assertEqual(123, self.edict.pop('b'))
		self.assertTrue('b' not in self.edict)

		self._assertEqualLogsSize(2)

		self._assertEqualLogs(self.edict._p_logs[1:], [
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__delitem__(key='b')", args=(), kwargs={'key': 'b'})
		])

	def test_popitem(self):
		self.assertEqual(('a', True), self.edict.popitem())
		self.assertTrue('a' not in self.edict)

		self._assertEqualLogsSize(2)

		self._assertEqualLogs(self.edict._p_logs[1:], [
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__delitem__(key='a')", args=(), kwargs={'key': 'a'})
		])


if __name__ == '__main__':
	unittest.main()
