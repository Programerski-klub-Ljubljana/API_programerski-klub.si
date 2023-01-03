import unittest
from dataclasses import dataclass

from core.domain._entity import Log, Edict, Elist, Elog
from core.domain._enums import LogLevel, LogType
from test.tutils import EntitySmall


@dataclass
class E(Elog):
	v: int


class test_Elog(unittest.TestCase):
	def setUp(self) -> None:
		self.elog = E(0)
		self.elog._logs = []
		self._assertEqualLogs(0)

	def _assertEqualLogs(self, size: int):
		self.assertEqual(len(self.elog._logs), size)
		self.assertEqual(len(self.elog.logs), size)
		self.assertEqual(self.elog.logs, self.elog._logs)

	def test_init(self):
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
		}
		data_out = Elog.init(data=data, logs=True)

		self.assertEqual(data, data_out)
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

	def test_is_logging(self):
		self.assertTrue(self.elog.is_logging)

		self.elog._p_log = False
		self.assertFalse(self.elog.is_logging)
		self.elog._p_log = True
		self.assertTrue(self.elog.is_logging)

		delattr(self.elog, '_logs')
		self.assertFalse(self.elog.is_logging)
		self.elog.__dict__['_logs'] = []
		self.assertTrue(self.elog.is_logging)

	def test_log_type(self):
		self.assertEqual(self.elog.log_type, LogType.ENTITY)

	def test_log(self):
		entity = EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'})

		self.elog.log(
			level=LogLevel.DEBUG, type=LogType.ELIST, msg='msg0',
			a=True, b=1, c=2.34, d='sadf',
			e=entity,
			f=[1, 2, 3],
			g={'a': 'b'})

		self._assertEqualLogs(1)

		self.assertEqual(self.elog.logs[0], Log(
			level=LogLevel.DEBUG, type=LogType.ELIST, msg='msg0',
			data=Edict(data={
				'a': True, 'b': 1, 'c': 2.34, 'd': 'sadf',
				'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}),
				'f': [1, 2, 3], 'g': {'a': 'b'}
			})
		))

	def test_log_call(self):
		entity = EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'})

		self.elog.log_call(
			self.test_log_call,
			type=LogType.EDICT,
			a=True, b=1, c=2.34, d='sadf',
			e=entity, f=[1, 2, 3], g={'a': 'b'})

		self._assertEqualLogs(1)

		self.assertEqual(
			self.elog.logs[0],
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
				data=Edict(data={
					'a': True, 'b': 1, 'c': 2.34, 'd': 'sadf',
					'e': EntitySmall(a=False, b=3, c=38.2, d='we3', e=None, f=[1], g={'a': 'b'}),
					'f': [1, 2, 3], 'g': {'a': 'b'}
				})))
		count = len(LogLevel.values())
		self.assertGreater(count, 3)
		self._assertEqualLogs(count)
