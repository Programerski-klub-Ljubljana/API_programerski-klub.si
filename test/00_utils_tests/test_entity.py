import unittest
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime

from persistent.list import PersistentList

from core.domain._entity import Elist, Entity, elist, Log, edict, Edict, Elog
from core.domain._enums import LogLevel, LogType
from test.tutils import EntityBig, Entity_fixtures, EntitySmall


@dataclass
class FakeEntity(Entity):
	a: str
	b: str = 'b'
	c: elist = Elist.field(data=[1, 2, 3])
	d: edict = Edict.field(data={'a': 'a', 'b': 1})


class test_Entity(unittest.TestCase):
	def _assertEqualLogs(self, arr1, arr2):
		arr1 = deepcopy(arr1)
		arr2 = deepcopy(arr2)

		for l in arr1 + arr2:
			l.created = 'now'
		self.assertEqual(arr1, arr2)

	def _assertEqualLogsSize(self, size: int):
		self.assertEqual(len(self.entity._p_logs), size)
		self.assertEqual(len(self.entity.logs), size)
		self.assertEqual(self.entity.logs, self.entity._p_logs)

	@classmethod
	def setUp(self) -> None:
		self.before = datetime.now()
		self.entity: EntityBig = Entity_fixtures.entity(cls=EntityBig, level=2)
		self.after = datetime.now()

	def test_init(self):
		# * TEST INSTANCE TYPE
		self.assertIsInstance(self.entity, Elog)
		self.assertIsInstance(self.entity, Entity)

		# * TEST PRIVATE LOG VARS
		self.assertEqual(self.entity._p_log, True)
		self.assertIsInstance(self.entity._p_logs, PersistentList)
		self.assertTrue(self.before < self.entity._p_created < self.after)
		self.assertTrue(self.before < self.entity._p_updated < self.after)

		# * TEST PRIVATE VARS
		self.assertGreater(len(self.entity._id), 20)
		self.assertEqual(self.entity._type, "entitybig")
		self.assertEqual(self.entity._connections, Elist())

		self._assertEqualLogsSize(1)
		init_log = self.entity._p_logs[0]
		self.assertEqual(init_log.level, LogLevel.DEBUG)
		self.assertEqual(init_log.type, LogType.ENTITY_INIT)
		self.assertTrue(self.before < init_log.created < self.after)
		self.assertEqual(init_log.args, [])

		self.assertEqual(str(init_log.kwargs)[:300],
		                 "{'a': True, 'b': 32, 'c': 0.23, 'd': 'asd', 'e': EntityBig(a=True, b=32, c=0.23, d='asd', e=EntityBig(a=True, b=32, c=0.23, d='asd', e=None, f=None, g=None, h=None, j=EntitySmall(a=True, b=32, c=0.23, d='asd', e=EntitySmall(a=True, b=32, c=0.23, d='asd', e=EntitySmall(a=True, b=32, c=0.23, d='asd', ")

		self.assertEqual(str(init_log.kwargs)[-300:],
		                 " [3.21, False, 321, 'mata', EntitySmall(a=True, b=32, c=0.23, d='asd', e=None, f=None, g=None, h=None), [3.21, False, 321, 'mata', None, None, None, None], {'a': True, 'b': 123, 'c': 1.23, 'd': 'data', 'e': None, 'f': None, 'g': None, 'h': None}, [3.21, False, 321, 'mata', None, None, None, None]]}}")

		self.assertEqual(init_log.msg[:300],
		                 "__init__(a=True, b=32, c=0.23, d='asd', e=EntityBig(a=True, b=32, c=0.23, d='asd', e=EntityBig(a=True, b=32, c=0.23, d='asd', e=None, f=None, g=None, h=None, j=EntitySmall(a=True, b=32, c=0.23, d='asd', e=EntitySmall(a=True, b=32, c=0.23, d='asd', e=EntitySmall(a=True, b=32, c=0.23, d='asd', e=None,")

		self.assertEqual(init_log.msg[-300:],
		                 " [3.21, False, 321, 'mata', EntitySmall(a=True, b=32, c=0.23, d='asd', e=None, f=None, g=None, h=None), [3.21, False, 321, 'mata', None, None, None, None], {'a': True, 'b': 123, 'c': 1.23, 'd': 'data', 'e': None, 'f': None, 'g': None, 'h': None}, [3.21, False, 321, 'mata', None, None, None, None]]})")

	def test_log_type(self):
		self.assertEqual(self.entity.log_type, LogType.ENTITY)

	def test_data(self):
		# * LEVEL 0
		self.assertEqual(self.entity.a, True)
		self.assertEqual(self.entity.b, 32)
		self.assertEqual(self.entity.c, 0.23)
		self.assertEqual(self.entity.d, 'asd')

		# * LEVEL 1: ENTITY
		self.assertIsInstance(self.entity.e, EntityBig)
		self.assertEqual(self.entity.e.a, True)
		self.assertEqual(self.entity.e.d, 'asd')
		# * LEVEL 2: -> ENTITY
		self.assertIsInstance(self.entity.e.e, EntityBig)
		self.assertEqual(self.entity.e.e.d, 'asd')
		# * LEVEL 2: -> ELIST
		self.assertIsInstance(self.entity.e.f, Elist)
		self.assertEqual(self.entity.e.f[2], 321)
		# * LEVEL 2: -> EDICT
		self.assertIsInstance(self.entity.e.g, Edict)
		self.assertEqual(self.entity.e.g['b'], 123)
		# * LEVEL 2: -> TUPLE
		self.assertIsInstance(self.entity.e.h, Elist)
		self.assertEqual(self.entity.e.f[0], 3.21)

		# * LEVEL 1: ELIST
		self.assertIsInstance(self.entity.f, Elist)
		self.assertEqual(self.entity.f[0], 3.21)
		self.assertEqual(self.entity.f[3], 'mata')
		# * LEVEL 2: -> ENTITY
		self.assertIsInstance(self.entity.f[4], EntityBig)
		self.assertEqual(self.entity.f[4].d, 'asd')
		# * LEVEL 2: -> ELIST
		self.assertIsInstance(self.entity.f[5], Elist)
		self.assertEqual(self.entity.f[5][2], 321)
		# * LEVEL 2: -> EDICT
		self.assertIsInstance(self.entity.f[6], Edict)
		self.assertEqual(self.entity.f[6]['b'], 123)
		# * LEVEL 2: -> TUPLE
		self.assertIsInstance(self.entity.f[7], Elist)
		self.assertEqual(self.entity.f[7][2], 321)

		# * LEVEL 1: EDICT
		self.assertIsInstance(self.entity.g, Edict)
		self.assertEqual(self.entity.g['b'], 123)
		self.assertEqual(self.entity.g['c'], 1.23)
		# * LEVEL 2: -> ENTITY
		self.assertIsInstance(self.entity.g['e'], EntityBig)
		self.assertEqual(self.entity.g['e'].d, 'asd')
		# * LEVEL 2: -> ELIST
		self.assertIsInstance(self.entity.g['f'], Elist)
		self.assertEqual(self.entity.g['f'][2], 321)
		# * LEVEL 2: -> EDICT
		self.assertIsInstance(self.entity.g['g'], Edict)
		self.assertEqual(self.entity.g['g']['b'], 123)
		# * LEVEL 2: -> TUPLE
		self.assertIsInstance(self.entity.g['h'], Elist)
		self.assertEqual(self.entity.g['h'][2], 321)

	def test_setattr(self):
		# * LEVEL 1 (SHOULD LOGS)
		self.entity.b = 321
		self.entity.e = EntitySmall(a=False, b=1234, c=1.234, d='new', e=None, f=None, g=None, h=None)
		self.entity.c = [[1, 2, 3], {'a': 'a'}]

		self.assertEqual(self.entity.b, 321)
		self.assertEqual(self.entity.e.b, 1234)
		self.assertEqual(self.entity.c, [[1, 2, 3], {'a': 'a'}])

		# * IT SHOULD CONVERT INNER STRUCTURE TO RIGHT OBJECT
		self.assertIsInstance(self.entity.c, Elist)
		self.assertIsInstance(self.entity.c[0], Elist)
		self.assertIsInstance(self.entity.c[1], Edict)

		# * LEVEL 2 (SHOULD LOGS)
		self.entity.f[0] = 12.3
		self.entity.g['b'] = 987

		self.assertEqual(self.entity.f[0], 12.3)
		self.assertEqual(self.entity.g['b'], 987)

		# * LEVEL 3 (SHOULD NOT LOGS)
		self.entity.h[4].b = 983
		self.entity.h[5][3] = 'asdfasd'

		self.assertEqual(self.entity.h[4].b, 983)
		self.assertEqual(self.entity.h[5][3], 'asdfasd')

		self.assertEqual(len(self.entity._p_logs), 4)
		self.assertEqual(len(self.entity.logs), 6)

		all_logs = [
			Log(
				level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__setattr__(key='b', value=321)", created='now', args=(),
				kwargs={'key': 'b', 'value': 321}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ENTITY,
				msg="__setattr__(key='e', value=EntitySmall(a=False, b=1234, c=1.234, d='new', e=None, f=None, g=None, h=None))", created='now',
				args=(), kwargs={'key': 'e', 'value': EntitySmall(a=False, b=1234, c=1.234, d='new', e=None, f=None, g=None, h=None)}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__setattr__(key='c', value=[[1, 2, 3], {'a': 'a'}])", created='now', args=(),
				kwargs={'key': 'c', 'value': [[1, 2, 3], {'a': 'a'}]}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST, msg='f.__setitem__(i=0, item=12.3)', created='now', args=(), kwargs={'i': 0, 'item': 12.3}),
			Log(
				level=LogLevel.DEBUG, type=LogType.EDICT, msg="g.__setitem__(key='b', item=987)", created='now', args=(),
				kwargs={'item': 987, 'key': 'b'})
		]

		self._assertEqualLogs(self.entity._p_logs[1:], all_logs[:3])
		self._assertEqualLogs(self.entity.logs[1:], all_logs)

	def test_equal(self):
		equal_entity = Entity_fixtures.entity(EntityBig, level=2)
		not_equal_entity = Entity_fixtures.entity(EntityBig, level=2)
		not_equal_entity.e.e.b = 1234

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

		self._assertEqualLogs(entity.logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ENTITY_INIT, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})", created='now',
				args=(),
				kwargs={'a': 'a', 'b': 'b', 'c': [1, 2, 3], 'd': {'a': 'a', 'b': 1}}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST, msg="_connections.append(item=FakeEntity(a='b', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1}))",
				created='now',
				args=(), kwargs={'item': FakeEntity(a='b', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})})
		])
		self._assertEqualLogs(entity1.logs, [
			Log(
				level=LogLevel.DEBUG, type=LogType.ENTITY_INIT, msg="__init__(a='b', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})", created='now',
				args=(), kwargs={'a': 'b', 'b': 'b', 'c': [1, 2, 3], 'd': {'a': 'a', 'b': 1}}),
			Log(
				level=LogLevel.DEBUG, type=LogType.ELIST, msg="_connections.append(item=FakeEntity(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1}))",
				created='now', args=(), kwargs={'item': FakeEntity(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})})
		])


if __name__ == '__main__':
	unittest.main()
