import unittest

from core.domain._entity import Log, Edict, Elist, Elog
from core.domain._enums import LogLevel, LogType
from test.tutils import Entity_fixtures, EntityBig, EntitySmall


class test_Edict(unittest.TestCase):
	def setUp(cls) -> None:
		data = Entity_fixtures.dict(EntityBig, level=2)
		cls.edict = Edict(data=data)

	def _assertEqualLogs(self, size: int):
		self.assertEqual(len(self.edict._logs), size)
		self.assertEqual(len(self.edict.logs), size)
		self.assertEqual(self.edict.logs, self.edict._logs)

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

	def test_init_is_logging(self):
		self.assertTrue(self.edict.is_logging)
		self.edict._p_log = False
		self.assertFalse(self.edict.is_logging)
		self.edict._p_log = True
		self.assertTrue(self.edict.is_logging)
		del self.edict._logs
		self.assertFalse(self.edict.is_logging)
		self.edict.__dict__['_logs'] = None
		self.assertTrue(self.edict.is_logging)
		Elog._p_log = False
		self.assertTrue(self.edict.is_logging)

	def test_init_logs(self):
		self._assertEqualLogs(1)

		self.assertEqual(
			self.edict._logs[0].msg[:100], "__init__(a=True, b=123, c=1.23, d='data', e=EntityBig(a=True, b=32, c=0.23, d='asd', e=EntityBig(a=T")
		self.assertEqual(
			self.edict._logs[0].msg[-100:], ", None, None], 'g': {'a': True, 'b': 123, 'c': 1.23, 'd': 'data', 'e': None, 'f': None, 'g': None}})")

	def test_log_type(self):
		self.assertEqual(self.edict.log_type, LogType.EDICT)

	def test_log(self):
		self._assertEqualLogs(1)

		entity = EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'})

		self.edict.log(
			level=LogLevel.DEBUG, type=LogType.ELIST, msg='msg0',
			a=True, b=1, c=2.34, d='sadf',
			e=entity,
			f=[1, 2, 3],
			g={'a': 'b'})

		self._assertEqualLogs(2)

		self.assertEqual(self.edict.logs[1], Log(
			level=LogLevel.DEBUG, type=LogType.ELIST, msg='msg0',
			data=Edict(data={
				'a': True, 'b': 1, 'c': 2.34, 'd': 'sadf',
				'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}),
				'f': [1, 2, 3], 'g': {'a': 'b'}
			})
		))

	def test_log_call(self):
		self._assertEqualLogs(1)

		entity = EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'})

		self.edict.log_call(
			self.test_log_call,
			type=LogType.EDICT,
			a=True, b=1, c=2.34, d='sadf',
			e=entity, f=[1, 2, 3], g={'a': 'b'})

		self._assertEqualLogs(2)

		self.assertEqual(
			self.edict.logs[1],
			Log(
				level=LogLevel.DEBUG,
				type=LogType.EDICT,
				msg=''.join([
					"test_log_call(a=True, b=1, c=2.34, d='sadf', ",
					"e=EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}), ",
					"f=[1, 2, 3], ",
					"g={'a': 'b'})"
				]),
				data=Edict(data={
					'a': True, 'b': 1, 'c': 2.34, 'd': 'sadf',
					'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}),
					'f': [1, 2, 3], 'g': {'a': 'b'}
				})))

	def test_log_levels(self):
		self._assertEqualLogs(1)

		log_args = {
			'type': LogType.EDICT,
			'msg': 'msg',
			'a': True,
			'b': 1,
			'c': 2.34,
			'd': 'sadf',
			'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}),
			'f': [1, 2, 3],
			'g': {'a': 'b'}
		}

		level_mapping = {
			self.edict.log_debug: LogLevel.DEBUG,
			self.edict.log_info: LogLevel.INFO,
			self.edict.log_warning: LogLevel.WARNING,
			self.edict.log_error: LogLevel.ERROR
		}

		for log_fun, log_level in level_mapping.items():
			log_fun(**log_args)

			self.assertEqual(
				self.edict.logs[-1],
				Log(
					level=log_level,
					type=LogType.EDICT,
					msg='msg',
					data=Edict(data={
						'a': True, 'b': 1, 'c': 2.34, 'd': 'sadf',
						'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}),
						'f': [1, 2, 3], 'g': {'a': 'b'}
					})))
		self._assertEqualLogs(1 + len(LogLevel.values()))

	def test_setitem(self):
		self.edict['a'] = False
		self.edict['b'] = 321
		self.edict['c'] = 32.1
		self.edict['d'] = 'hehe'
		# ! CE UPORABNIK NASTAVI VREDNOSTI PREKO METOD JE POTREBNO NOTRANJO STRUKTURO TUDI PRETVORITI V EDICT, ELIST OBLIKO

"""
	def test_setitem(self):
		self.edict['d'] = E(4)
		self.assertEqual(self.edict, {'a': E(1), 'b': E(2), 'c': E(3), 'd': E(4)})
		self.assertEqual(self.edict._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(a=E(value=1), b=E(value=2), c=E(value=3))'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="__setitem__(key='d', item=E(value=4))")
		])

	def test_delitem(self):
		del self.edict['a']
		self.assertEqual(self.edict, {'b': E(2), 'c': E(3)})
		self.assertEqual(self.edict._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(a=E(value=1), b=E(value=2), c=E(value=3))'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="__delitem__(key='a')")
		])

	def test_clear(self):
		self.edict.clear()
		self.assertEqual(self.edict, {})
		self.assertEqual(self.edict._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(a=E(value=1), b=E(value=2), c=E(value=3))'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="clear()")
		])

	def test_update(self):
		self.edict.update(c='4', d=E(5))
		self.assertEqual(self.edict, {'a': E(1), 'b': E(2), 'c': '4', 'd': E(5)})
		self.assertEqual(self.edict._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(a=E(value=1), b=E(value=2), c=E(value=3))'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="__setitem__(key='c', item='4')"),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="__setitem__(key='d', item=E(value=5))")
		])

	def test_setdefault(self):
		self.assertEqual(E(value=1), self.edict.setdefault('a', 'value'))
		self.assertEqual('value', self.edict.setdefault('x', 'value'))

		self.assertEqual(self.edict, {'a': E(1), 'b': E(2), 'c': E(3), 'x': 'value'})
		self.assertEqual(self.edict._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(a=E(value=1), b=E(value=2), c=E(value=3))'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="__setitem__(key='x', item='value')")
		])

	def test_pop(self):
		self.assertEqual(E(value=1), self.edict.pop('a'))
		self.assertEqual(self.edict, {'b': E(2), 'c': E(3)})
		self.assertEqual(self.edict._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(a=E(value=1), b=E(value=2), c=E(value=3))'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="__delitem__(key='a')")
		])

	def test_popitem(self):
		self.assertEqual(('a', E(value=1)), self.edict.popitem())
		self.assertEqual(self.edict, {'b': E(2), 'c': E(3)})
		self.assertEqual(self.edict._logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='__init__(a=E(value=1), b=E(value=2), c=E(value=3))'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="__delitem__(key='a')")
		])
"""

if __name__ == '__main__':
	unittest.main()
