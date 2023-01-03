import unittest

from core.domain._entity import Edict, Elist, Elog, Log
from core.domain._enums import LogType, LogLevel
from test.tutils import Entity_fixtures, EntityBig, EntitySmall


class test_Edict(unittest.TestCase):

	def _assertEqualLogs(self, size: int):
		self.assertEqual(len(self.edict._logs), size)
		self.assertEqual(len(self.edict.logs), size)
		self.assertEqual(self.edict.logs, self.edict._logs)

	def setUp(self) -> None:
		data = Entity_fixtures.dict(EntityBig, level=2)
		self.edict = Edict(data=data)
		self._assertEqualLogs(1)

	def test_is_logging(self):
		self.assertTrue(self.edict.is_logging)

	def test_logs(self):
		self.assertEqual(
			self.edict._logs[0].msg[:100], "__init__(a=True, b=123, c=1.23, d='data', e=EntityBig(a=True, b=32, c=0.23, d='asd', e=EntityBig(a=T")

	def test_log_type(self):
		self.assertEqual(self.edict.log_type, LogType.EDICT)

	def test_is_elog_instance(self):
		self.assertIsInstance(self.edict, Elog)

	def test_init(self):
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

		self.assertEqual(self.edict['b'], 321)
		self.assertEqual(self.edict['e'].b, 1234)

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

		self.assertEqual(len(self.edict._logs), 3)
		self.assertEqual(len(self.edict.logs), 5)

		all_logs = [
			Log(
				level=LogLevel.DEBUG, type=LogType.EDICT,
				msg="__setitem__(key='b', item=321)", data=Edict({'key': 'b', 'item': 321})),
			Log(
				level=LogLevel.DEBUG, type=LogType.EDICT,
				msg="__setitem__(key='e', item=EntitySmall(a=False, b=1234, c=1.234, d='new', e=None, f=None, g=None, h=None))",
				data=Edict({'item': EntitySmall(a=False, b=1234, c=1.234, d='new', e=None, f=None, g=None, h=None), 'key': 'e'})),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="['f'].__setitem__(i=0, item=12.3)", data=Edict({'i': 0, 'item': 12.3})),
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="['g'].__setitem__(key='b', item=987)", data=Edict({'key': 'b', 'item': 987}))
		]

		self.assertEqual(self.edict._logs[1:], all_logs[:2])
		self.assertEqual(self.edict.logs[1:], all_logs)

	def test_delitem(self):
		self.assertTrue('b' in self.edict)
		self.assertTrue('e' in self.edict)

		del self.edict['b']
		del self.edict['e']

		self.assertTrue('b' not in self.edict)
		self.assertTrue('e' not in self.edict)

		self._assertEqualLogs(3)

		self.assertEqual(self.edict.logs[1:], [
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__delitem__(key='b')", data=Edict({'key': 'b'})),
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__delitem__(key='e')", data=Edict({'key': 'e'})),
		])

	def test_clear(self):
		self.assertGreater(len(self.edict.data), 3)
		self.edict.clear()
		self.assertEqual(self.edict, {})

		self._assertEqualLogs(2)

		self.assertEqual(self.edict._logs[1:], [
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="clear()")
		])

	def test_update(self):
		self.assertTrue('x' not in self.edict)
		self.assertTrue('d' in self.edict)
		self.assertEqual(self.edict['d'], 'data')
		self.edict.update(x='4', d=5)
		self.assertEqual(self.edict['x'], '4')
		self.assertEqual(self.edict['d'], 5)

		self._assertEqualLogs(3)

		self.assertEqual(self.edict._logs[1:], [
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__setitem__(key='x', item='4')", data=Edict({'key': 'x', 'item': '4'})),
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__setitem__(key='d', item=5)", data=Edict({'key': 'd', 'item': 5}))
		])

	def test_setdefault(self):
		self.assertEqual(self.edict['a'], True)

		self.assertEqual(self.edict.setdefault('a', 'value'), True)
		self.assertEqual('value', self.edict.setdefault('x', 'value'))

		self.assertEqual(self.edict['a'], True)
		self.assertEqual(self.edict['x'], 'value')

		self._assertEqualLogs(2)

		self.assertEqual(self.edict._logs[1:], [
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__setitem__(key='x', item='value')", data=Edict({'key': 'x', 'item': 'value'}))
		])

	def test_pop(self):
		self.assertEqual(self.edict['b'], 123)
		self.assertEqual(123, self.edict.pop('b'))
		self.assertTrue('b' not in self.edict)

		self._assertEqualLogs(2)

		self.assertEqual(self.edict._logs[1:], [
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__delitem__(key='b')", data=Edict({'key': 'b'}))
		])

	def test_popitem(self):
		self.assertEqual(('a', True), self.edict.popitem())
		self.assertTrue('a' not in self.edict)

		self._assertEqualLogs(2)

		self.assertEqual(self.edict._logs[1:], [
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="__delitem__(key='a')", data=Edict({'key': 'a'}))
		])


if __name__ == '__main__':
	unittest.main()
