import unittest
from dataclasses import dataclass
from datetime import datetime, timedelta

from persistent.list import PersistentList

from core.domain._entity import Edict, Elist, Elog, Log
from core.domain._enums import LogLevel, LogType
from test.tutils import EntitySmall


@dataclass
class E(Elog):
	v: int

	@property
	def data(self):
		return self

	@property
	def __dict__(self):
		return {'v': self.v}


class test_Elog(unittest.TestCase):

	def _assertEqualLogs(self, size: int):
		self.assertEqual(len(self.elog._p_logs), size)
		self.assertEqual(len(self.elog.logs), size)
		self.assertEqual(self.elog.logs, self.elog._p_logs)

	def setUp(self) -> None:
		before = datetime.now() - timedelta(seconds=2)
		self.elog = E(0)
		after = datetime.now() + timedelta(seconds=2)

		self.assertTrue(before < self.elog._created < after)
		self.assertTrue(before < self.elog._p_updated < after)
		self._assertEqualLogs(0)

	def test_inheritance(self):
		self.assertIsInstance(self.elog, Elog)
		self.assertEqual(self.elog._p_log, True)
		self.assertEqual(self.elog._p_logs, PersistentList())
		self.assertIsInstance(self.elog._created, datetime)
		self.assertIsInstance(self.elog._p_updated, datetime)

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

	def test_log(self):
		entity = EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=(1, 2, 3))

		self.elog.log(
			level=LogLevel.DEBUG, type=LogType.ELIST, msg='msg0',
			a=True, b=1, c=2.34, d='sadf',
			e=entity,
			f=[1, 2, 3],
			g={'a': 'b'}, h=(1, 2, 3))

		self._assertEqualLogs(1)

		self.assertEqual(self.elog.logs[0], Log(
			level=LogLevel.DEBUG, type=LogType.ELIST, msg='msg0',
			data={
				'a': True, 'b': 1, 'c': 2.34, 'd': 'sadf',
				'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=(1, 2, 3)),
				'f': [1, 2, 3], 'g': {'a': 'b'}, 'h': (1, 2, 3)
			}))

	def test_log_outside_scope(self):
		e0 = E(0)
		e1 = E(e0)
		e2 = E(e1)
		self.elog = E(e2)
		self._assertEqualLogs(0)

		# * SHOULD LOGS ON FIRST LEVEL
		self.elog.log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='msg0', a='a', b='b')
		self._assertEqualLogs(1)
		self.assertEqual(self.elog.logs[-1], Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='msg0', data=Edict(data={'a': 'a', 'b': 'b'})))

		# * SHOULD LOGS ON SECOND LEVEL
		self.elog.v.log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='msg1', a='a', b='b')
		self.assertEqual(len(self.elog.logs), 2)
		self.assertEqual(len(self.elog._p_logs), len(self.elog.logs) - 1)
		self.assertEqual(self.elog.logs[-1], Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='v.msg1', data=Edict(data={'a': 'a', 'b': 'b'})))

		# * SHOULD NOT LOGS ON THIRD LEVEL
		self.elog.v.v.log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='msg2', a='a', b='b')
		self.assertEqual(len(self.elog.logs), 2)

	def test_log_call(self):
		entity = EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=(1, 2, 3))

		self.elog.log_call(
			self.test_log_call,
			type=LogType.EDICT,
			a=True, b=1, c=2.34, d='sadf',
			e=entity, f=[1, 2, 3], g={'a': 'b'}, h=(1, 2, 3))

		self._assertEqualLogs(1)

		self.assertEqual(
			self.elog.logs[0],
			Log(
				level=LogLevel.DEBUG,
				type=LogType.EDICT,
				msg=''.join([
					"test_log_call(a=True, b=1, c=2.34, d='sadf', ",
					"e=EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=[1, 2, 3]), ",
					"f=[1, 2, 3], ",
					"g={'a': 'b'}, h=(1, 2, 3))"
				]),
				data={
					'a': True, 'b': 1, 'c': 2.34, 'd': 'sadf',
					'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=(1, 2, 3)),
					'f': [1, 2, 3], 'g': {'a': 'b'}, 'h': (1, 2, 3)
				}))

	def test_log_call_outside_scope(self):
		e0 = E(0)
		e1 = E(e0)
		e2 = E(e1)
		self.elog = E(e2)
		self._assertEqualLogs(0)

		# * SHOULD LOGS ON FIRST LEVEL
		self.elog.log_call(method=self.test_log_outside_scope, type=LogType.ENTITY, a='a', b='b')
		self._assertEqualLogs(1)
		self.assertEqual(self.elog.logs[-1], Log(
			level=LogLevel.DEBUG, type=LogType.ENTITY, msg="test_log_outside_scope(a='a', b='b')", data=Edict(data={'a': 'a', 'b': 'b'})))

		# * SHOULD LOGS ON SECOND LEVEL
		self.elog.v.log_call(method=self.test_log_outside_scope, type=LogType.ENTITY, a='c', b='d')
		self.assertEqual(len(self.elog.logs), 2)
		self.assertEqual(len(self.elog._p_logs), len(self.elog.logs) - 1)
		self.assertEqual(self.elog.logs[-1], Log(
			level=LogLevel.DEBUG, type=LogType.ENTITY, msg="v.test_log_outside_scope(a='c', b='d')", data=Edict(data={'a': 'c', 'b': 'd'})))

		# * SHOULD NOT LOGS ON THIRD LEVEL
		self.elog.v.v.log_call(method=self.test_log_outside_scope, type=LogType.ENTITY, a='e', b='f')
		self.assertEqual(len(self.elog.logs), 2)

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

		for log_fun, log_level in level_mapping.items():
			log_fun(**log_args)

		self.assertEqual(
			self.elog.logs[-1],
			Log(
				level=log_level,
				type=LogType.EDICT,
				msg='msg',
				data={
					'a': True, 'b': 1, 'c': 2.34, 'd': 'sadf',
					'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}, h=(1, 2, 3)),
					'f': [1, 2, 3], 'g': {'a': 'b'}, 'h': (3, 2, 1)
				}))
		count = len(LogLevel.values())
		self.assertGreater(count, 3)
		self._assertEqualLogs(count)
