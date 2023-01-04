import unittest
from copy import deepcopy
from dataclasses import dataclass

from persistent.list import PersistentList

from core.domain._entity import Edict, Elist, Elog, Log, datetime
from core.domain._enums import LogLevel, LogType
from test.tutils import EntitySmall


@dataclass
class E(Elog):
	v: any

	def __post_init__(self):
		super(E, self).__post_init__(**self.__dict__)


class ElogTestCase(unittest.TestCase):
	def _assertEqualLogs(self, arr1, arr2):
		arr1 = deepcopy(arr1)
		arr2 = deepcopy(arr2)

		for l in arr1 + arr2:
			l.created = 'now'
		self.assertEqual(arr1, arr2)


class test_Elog(ElogTestCase):

	def _assertEqualLogsSize(self, size):
		self.assertEqual(len(self.elog._p_logs), size)
		self.assertEqual(self.elog._p_logs, self.elog.logs)

	def setUp(self) -> None:
		self.before = datetime.now()
		self.elog = E(0)
		self.after = datetime.now()

	def test_init(self):
		self.assertIsInstance(self.elog, Elog)

		self.assertEqual(self.elog._p_log, True)
		self.assertIsInstance(self.elog._p_logs, PersistentList)
		self.assertTrue(self.before < self.elog._p_created < self.after)
		self.assertTrue(self.before < self.elog._p_updated < self.elog.logs[0].created)

		self._assertEqualLogs(self.elog._p_logs, [
			Log(
				level=LogLevel.DEBUG,
				type=LogType.ENTITY_INIT,
				msg='__init__(v=0)', args=(), kwargs={'v': 0})
		])

	def test_init_with_dict(self):
		data = {
			'a': 'a',
			'b': [
				{
					'a': 'a',
					'b': {'a': 'a'},
					'c': [1, 2, 3],
					'd': (1, 2, 3),
					'e': {1, 2, 3},
				},
				[
					1,
					{'a': 'a'},
					[1, 2, 3],
					(1, 2, 3),
					{1, 2, 3},
				]
			],
			'c': {
				'a': 'a',
				'b': {'a': 'a'},
				'c': [1, 2, 3],
				'd': (1, 2, 3),
				'e': {1, 2, 3}
			},
			'd': (1, 2, 3),
			'e': {1, 2, 3},
		}
		data_out = Elog.init(data=data)

		self.assertEqual(data_out['b'][0]['b']['a'], data['b'][0]['b']['a'])
		self.assertEqual(data_out['b'][0]['c'][-1], data['b'][0]['c'][-1])
		self.assertEqual(data_out['b'][0]['d'][-1], data['b'][0]['d'][-1])
		self.assertEqual(data_out['b'][0]['e'][-1], data['b'][0]['e'][-1])
		self.assertEqual(data_out['b'][1][1]['a'], data['b'][1][1]['a'])
		self.assertEqual(data_out['b'][1][2][0], data['b'][1][2][0])
		self.assertEqual(data_out['b'][1][3][0], data['b'][1][3][0])
		self.assertEqual(data_out['b'][1][4][0], data['b'][1][4][0])
		self.assertEqual(data_out['c']['b']['a'], data['c']['b']['a'])
		self.assertEqual(data_out['c']['c'][1], data['c']['c'][1])
		self.assertEqual(data_out['c']['d'][1], data['c']['d'][1])
		self.assertEqual(data_out['c']['e'][1], list(data['c']['e'])[1])

		self.assertIsInstance(data_out, dict)
		self.assertIsInstance(data_out['b'], Elist)
		self.assertIsInstance(data_out['b'][0], Edict)
		self.assertIsInstance(data_out['b'][0]['b'], Edict)
		self.assertIsInstance(data_out['b'][0]['c'], Elist)
		self.assertIsInstance(data_out['b'][0]['d'], Elist)
		self.assertIsInstance(data_out['b'][0]['e'], Elist)
		self.assertIsInstance(data_out['b'][1], Elist)
		self.assertIsInstance(data_out['b'][1][1], Edict)
		self.assertIsInstance(data_out['b'][1][2], Elist)
		self.assertIsInstance(data_out['b'][1][3], Elist)
		self.assertIsInstance(data_out['b'][1][4], Elist)
		self.assertIsInstance(data_out['c']['b'], Edict)
		self.assertIsInstance(data_out['c']['c'], Elist)
		self.assertIsInstance(data_out['c']['d'], Elist)
		self.assertIsInstance(data_out['c']['e'], Elist)
		self.assertIsInstance(data_out['d'], Elist)
		self.assertIsInstance(data_out['e'], Elist)

	def test_init_with_list(self):
		data = [
			'a',
			[
				{
					'a': 'a',
					'b': {'a': 'a'},
					'c': [1, 2, 3],
					'd': (1, 2, 3),
					'e': {1, 2, 3},
				},
				[
					1,
					{'a': 'a'},
					[1, 2, 3],
					(1, 2, 3),
					{1, 2, 3},
				]
			],
			{
				'a': 'a',
				'b': {'a': 'a'},
				'c': [1, 2, 3],
				'd': (1, 2, 3),
				'e': {1, 2, 3}
			},
			(1, 2, 3),
			{1, 2, 3}
		]
		data_out = Elog.init(data=data)

		self.assertEqual(data_out[1][0]['b']['a'], data[1][0]['b']['a'])
		self.assertEqual(data_out[1][0]['c'][-1], data[1][0]['c'][-1])
		self.assertEqual(data_out[1][0]['d'][-1], data[1][0]['d'][-1])
		self.assertEqual(data_out[1][0]['e'][-1], data[1][0]['e'][-1])
		self.assertEqual(data_out[1][1][1]['a'], data[1][1][1]['a'])
		self.assertEqual(data_out[1][1][2][0], data[1][1][2][0])
		self.assertEqual(data_out[1][1][3][0], data[1][1][3][0])
		self.assertEqual(data_out[1][1][4][0], list(data[1][1][4])[0])
		self.assertEqual(data_out[2]['b']['a'], data[2]['b']['a'])
		self.assertEqual(data_out[2]['c'][1], data[2]['c'][1])
		self.assertEqual(data_out[2]['d'][1], data[2]['d'][1])
		self.assertEqual(data_out[2]['e'][1], list(data[2]['e'])[1])

		self.assertIsInstance(data_out, list)
		self.assertIsInstance(data_out[1], Elist)
		self.assertIsInstance(data_out[1][0], Edict)
		self.assertIsInstance(data_out[1][0]['b'], Edict)
		self.assertIsInstance(data_out[1][0]['c'], Elist)
		self.assertIsInstance(data_out[1][0]['d'], Elist)
		self.assertIsInstance(data_out[1][0]['e'], Elist)
		self.assertIsInstance(data_out[1][1], Elist)
		self.assertIsInstance(data_out[1][1][1], Edict)
		self.assertIsInstance(data_out[1][1][2], Elist)
		self.assertIsInstance(data_out[1][1][3], Elist)
		self.assertIsInstance(data_out[1][1][4], Elist)
		self.assertIsInstance(data_out[2]['b'], Edict)
		self.assertIsInstance(data_out[2]['c'], Elist)
		self.assertIsInstance(data_out[2]['d'], Elist)
		self.assertIsInstance(data_out[2]['e'], Elist)
		self.assertIsInstance(data_out[3], Elist)
		self.assertIsInstance(data_out[4], Elist)

	def test_logs(self):
		es = EntitySmall(
			a=False, b=321, c=3.21, d='trs',
			e=EntitySmall(a=False, b=321, c=3.21, d='trs', e=EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None), f=None,
			              g=None, h=None),
			f=Elist([1, 2, 3, EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None)]),
			g=Edict({'a': 'a', 'b': EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None)}), h=None)

		# * FIRST LEVEL CHANGES
		es.e.a = True  # ! SHOULD LOGS
		es.e.e.b = 123  # ! SHOULD NOT LOGS

		# * SECOND LEVEL CHANGES
		es.f[3].b = 123
		es.g['b'].b = 123

		# * CHECK FIRST LEVEL CHANGES
		logs = es.logs
		self.assertIsInstance(logs, list)
		self._assertEqualLogs(es._p_logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ENTITY_INIT,
				msg=''.join([
					"__init__(a=False, b=321, c=3.21, d='trs', ",
					"e=EntitySmall(",
					"a=False, b=321, c=3.21, d='trs', e=EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None), "
					"f=None, g=None, h=None), ",
					"f=[1, 2, 3, EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None)], ",
					"g={'a': 'a', 'b': EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None)}, h=None)"
				]), created='now', args=(),
				kwargs={
					'a': False, 'b': 321, 'c': 3.21, 'd': 'trs',
					'e': EntitySmall(
						a=False, b=321, c=3.21, d='trs', e=EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None),
						f=None, g=None, h=None),
					'f': [1, 2, 3, EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None)],
					'g': {'a': 'a', 'b': EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None)}, 'h': None})])
		self._assertEqualLogs(logs, es._p_logs + [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY,
			    msg="e.__setattr__(key='a', value=True)", created='now', args=(), kwargs={'key': 'a', 'value': True})
		])

		# * CHECK SECOND LEVEL CHANGES ELIST
		logs = es.f.logs
		self.assertIsInstance(logs, list)
		self._assertEqualLogs(es.f._p_logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST_INIT,
				msg="__init__(1, 2, 3, EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None))",
				created='now', args=(1, 2, 3, EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None)), kwargs={})
		])
		self._assertEqualLogs(logs, es.f._p_logs + [
			Log(
				level=LogLevel.DEBUG, type=LogType.ENTITY, msg="[3].__setattr__(key='b', value=123)", created='now', args=(),
				kwargs={'key': 'b', 'value': 123})
		])

		# * CHECK SECOND LEVEL CHANGES DICT
		logs = es.g.logs
		self.assertIsInstance(logs, list)
		self._assertEqualLogs(es.g._p_logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.EDICT_INIT,
				msg="__init__(a='a', b=EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None))",
				created='now', args=(), kwargs={'a': 'a', 'b': EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None)})
		])
		self._assertEqualLogs(logs, es.g._p_logs + [
			Log(
				level=LogLevel.DEBUG, type=LogType.ENTITY,
				msg="['b'].__setattr__(key='b', value=123)", created='now', args=(), kwargs={'key': 'b', 'value': 123})
		])

	def test_log_type(self):
		e = EntitySmall(a=False, b=321, c=3.21, d='trs', e=None, f=None, g=None, h=None)
		f = Elist([1, 2, 3])
		g = Edict({'a': 'a'})

		e.a = False
		f[0] = 0
		g['a'] = 'b'

		self.assertEqual(self.elog.log_type, LogType.ENTITY)
		self.assertEqual(e.log_type, LogType.ENTITY)
		self.assertEqual(f.log_type, LogType.ELIST)
		self.assertEqual(g.log_type, LogType.EDICT)

		self.assertEqual(self.elog._p_logs[0].type, LogType.ENTITY_INIT)
		self.assertEqual(e._p_logs[0].type, LogType.ENTITY_INIT)
		self.assertEqual(f._p_logs[0].type, LogType.ELIST_INIT)
		self.assertEqual(g._p_logs[0].type, LogType.EDICT_INIT)

		self.assertEqual(e._p_logs[1].type, LogType.ENTITY)
		self.assertEqual(f._p_logs[1].type, LogType.ELIST)
		self.assertEqual(g._p_logs[1].type, LogType.EDICT)

	def test_log(self):
		entity = EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=(1, 2, 3))

		before_change = datetime.now()
		self.elog.log(
			level=LogLevel.DEBUG, type=LogType.ELIST, msg='msg0', args=[1, 1.3, "str", entity],
			a=True, b=1, c=2.34, d='sadf',
			e=entity,
			f=[1, 2, 3],
			g={'a': 'b'}, h=(1, 2, 3))
		after_change = datetime.now()

		self.assertTrue(self.before < self.elog._p_created < self.after)

		# * TEST IF DATE IS UPDATED!
		self.assertFalse(self.before < self.elog._p_updated < self.after)
		self.assertTrue(before_change < self.elog._p_updated < after_change)

		self._assertEqualLogs(self.elog.logs[1:], [
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST, msg='msg0',
				args=(1, 1.3, "str", entity),
				kwargs={
					'a': True, 'b': 1, 'c': 2.34, 'd': 'sadf',
					'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=(1, 2, 3)),
					'f': [1, 2, 3], 'g': {'a': 'b'}, 'h': (1, 2, 3)
				})
		])

	def test_log_outside_scope(self):
		e0 = E(0)
		e1 = E(e0)
		e2 = E(e1)
		self.elog = E(e2)
		self._assertEqualLogsSize(1)

		# * SHOULD LOGS ON FIRST LEVEL
		self.elog.log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='msg0', a='a', b='b')
		self._assertEqualLogsSize(2)
		self._assertEqualLogs([self.elog.logs[-1]],
		                      [Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='msg0', args=(), kwargs={'a': 'a', 'b': 'b'})])

		# * SHOULD LOGS ON SECOND LEVEL
		self.elog.v.log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='msg1', a='a', b='b')
		self.assertEqual(len(self.elog.logs), 3)
		self.assertEqual(len(self.elog._p_logs), len(self.elog.logs) - 1)
		self._assertEqualLogs([self.elog.logs[-1]],
		                      [Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='v.msg1', args=(), kwargs={'a': 'a', 'b': 'b'})])

		# * SHOULD NOT LOGS ON THIRD LEVEL
		self.elog.v.v.log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='msg2', a='a', b='b')
		self.assertEqual(len(self.elog.logs), 3)

	def test_log_call(self):
		entity = EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=(1, 2, 3))

		self.elog.log_call(
			self.test_log_call,
			type=LogType.EDICT,
			a=True, b=1, c=2.34, d='sadf',
			e=entity, f=[1, 2, 3], g={'a': 'b'}, h=(1, 2, 3))

		self.elog.log_call(self.test_log_call, type=LogType.EDICT)
		self.elog.log_call(self.test_log_call, type=LogType.EDICT, args=(1, 2))
		self.elog.log_call(self.test_log_call, type=LogType.EDICT, key='key')
		self.elog.log_call(self.test_log_call, type=LogType.EDICT, args=(1,), key='key')

		self._assertEqualLogsSize(6)

		self._assertEqualLogs(self.elog.logs[1:], [
			Log(
				level=LogLevel.DEBUG,
				type=LogType.EDICT,
				msg=''.join([
					"test_log_call(a=True, b=1, c=2.34, d='sadf', ",
					"e=EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=[1, 2, 3]), ",
					"f=[1, 2, 3], ",
					"g={'a': 'b'}, h=(1, 2, 3))"
				]),
				args=(),
				kwargs={
					'a': True, 'b': 1, 'c': 2.34, 'd': 'sadf',
					'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=(1, 2, 3)),
					'f': [1, 2, 3], 'g': {'a': 'b'}, 'h': (1, 2, 3)
				}),
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg='test_log_call()', created='now', args=(), kwargs={}),
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg='test_log_call(1, 2)', created='now', args=(1, 2), kwargs={}),
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="test_log_call(key='key')", created='now', args=(), kwargs={'key': 'key'}),
			Log(level=LogLevel.DEBUG, type=LogType.EDICT, msg="test_log_call(1, key='key')", created='now', args=(1,), kwargs={'key': 'key'})
		])

	def test_log_call_outside_scope(self):
		e0 = E(0)
		e1 = E(e0)
		e2 = E(e1)
		self.elog = E(e2)
		self._assertEqualLogsSize(1)

		# * SHOULD LOGS ON FIRST LEVEL
		self.elog.log_call(method=self.test_log_outside_scope, type=LogType.ENTITY, a='a', b='b')
		self._assertEqualLogsSize(2)
		self._assertEqualLogs(self.elog.logs[1:], [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="test_log_outside_scope(a='a', b='b')", args=(), kwargs={'a': 'a', 'b': 'b'})
		])

		# * SHOULD LOGS ON SECOND LEVEL
		self.elog.v.log_call(method=self.test_log_outside_scope, type=LogType.ENTITY, a='c', b='d')
		self.assertEqual(len(self.elog.logs), 3)
		self.assertEqual(len(self.elog._p_logs), len(self.elog.logs) - 1)
		self._assertEqualLogs(self.elog.logs[2:], [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="v.test_log_outside_scope(a='c', b='d')", args=(), kwargs={'a': 'c', 'b': 'd'})
		])

		# * SHOULD NOT LOGS ON THIRD LEVEL
		self.elog.v.v.log_call(method=self.test_log_outside_scope, type=LogType.ENTITY, a='e', b='f')
		self.assertEqual(len(self.elog.logs), 3)

	def test_log_levels(self):
		log_args = {
			'type': LogType.EDICT,
			'msg': 'msg',
			'a': True,
			'b': 1,
			'c': 2.34,
			'd': 'sadf',
			'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=(1, 2, 3)),
			'f': [1, 2, 3],
			'g': {'a': 'b'},
			'h': (3, 2, 1)
		}

		level_mapping = {
			self.elog.log_debug: LogLevel.DEBUG,
			self.elog.log_info: LogLevel.INFO,
			self.elog.log_warning: LogLevel.WARNING,
			self.elog.log_error: LogLevel.ERROR
		}

		for i, (log_fun, log_level) in enumerate(level_mapping.items()):
			log_fun(**log_args)

			self._assertEqualLogs(
				[self.elog.logs[-1]],
				[Log(
					level=log_level,
					type=LogType.EDICT,
					msg='msg',
					args=(),
					kwargs={
						'a': True, 'b': 1, 'c': 2.34, 'd': 'sadf',
						'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=(1, 2, 3)),
						'f': [1, 2, 3], 'g': {'a': 'b'}, 'h': (3, 2, 1)
					})
				])

			self._assertEqualLogsSize(2 + i)
