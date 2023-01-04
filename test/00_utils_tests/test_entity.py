import unittest
from dataclasses import dataclass
from datetime import datetime

import shortuuid

from core.domain._entity import Elist, Entity, elist, Log, edict, Edict
from core.domain._enums import LogLevel, LogType


@dataclass
class FakeEntity(Entity):
	a: str
	b: str = 'b'
	c: elist = Elist.field(data=[1, 2, 3])
	d: edict = Edict.field(data={'a': 'a', 'b': 1})


class test_Entity(unittest.TestCase):
	@classmethod
	def setUp(self) -> None:
		self.before = datetime.now()
		self.entity: FakeEntity = FakeEntity(a='a', c=[1, 2, 3])
		self.after = datetime.now()

	def test_attr(self):
		self.assertTrue(self.entity.a, 'a')
		self.assertTrue(self.entity.b, 'b')
		self.assertTrue(self.entity.c, Elist([1, 2, 3]))
		self.assertTrue(self.entity.d, Edict({'a': 'a', 'b': 1}))

		self.assertEqual(len(self.entity._id), len(shortuuid.uuid()))
		self.assertEqual(self.entity._type, "fakeentity")
		self.assertTrue(self.before < self.entity._p_created < self.after)
		self.assertTrue(self.before < self.entity._p_updated < self.after)

		self.assertIsInstance(self.entity._connections, Elist)
		self.assertEqual(self.entity._connections, [])

		self.assertIsInstance(self.entity._p_logs, Elist)
		self.assertEqual(self.entity._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})")
		])

		self.assertEqual(len(self.entity.__dict__), 10)

	def test_setattr(self):
		self.assertEqual(self.entity.a, 'a')
		self.assertEqual(self.entity._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})")
		])

		self.entity.a = 'b'
		self.assertEqual(self.entity.a, 'b')
		self.assertEqual(self.entity._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="a = 'b'"),
		])

		setattr(self.entity, 'a', 10)
		self.assertEqual(self.entity.a, 10)
		self.assertEqual(self.entity._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="a = 'b'"),
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='a = 10')
		])

		# ! TEST PRIVATE PROPERTIES
		self.entity._p_test = 123
		self.assertEqual(self.entity._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="a = 'b'"),
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='a = 10')
		])

	def test_delattr(self):
		with self.assertRaises(Exception):
			del self.entity.a
		with self.assertRaises(Exception):
			delattr(self.entity, 'a')

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
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY,
			    msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST,
			    msg="_connections.append(item=FakeEntity(a='b', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1}))")])
		self.assertEqual(entity1.logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY,
			    msg="__init__(a='b', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST,
			    msg="_connections.append(item=FakeEntity(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1}))")])

	def test_logs(self):
		self.entity.a = 'b'
		self.entity.c.append(4)
		self.entity.c.append('4')
		self.entity.c.remove('4')
		self.entity.d['x'] = 'y'
		self.assertEqual(self.entity.logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="a = 'b'"),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='c.append(item=4)'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="c.append(item='4')"),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="c.remove(item='4')"),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="d.__setitem__(key='x', item='y')")
		])

	def test_logs_property(self):
		self.assertEqual(self.entity.logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
		])
		self.entity.a = 'new a'
		self.entity.c.append('new c')
		self.entity.b = 'new b'
		self.entity.c.append(123)
		logs = self.entity.logs
		self.assertEqual(logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="a = 'new a'"),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg="c.append(item='new c')"),
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="b = 'new b'"),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='c.append(item=123)')
		])

		for i in range(len(logs) - 1):
			self.assertGreater(logs[i + 1]._p_created, logs[i]._p_created)

	def test_log(self):
		self.entity.log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='msg0')
		self.entity.log(level=LogLevel.INFO, type=LogType.ELIST, msg='msg1')
		self.entity.log(level=LogLevel.WARNING, type=LogType.ENTITY, msg='msg2')
		self.entity.log(level=LogLevel.ERROR, type=LogType.ELIST, msg='msg3')

		self.assertEqual(self.entity._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='msg0'),
			Log(level=LogLevel.INFO, type=LogType.ELIST, msg='msg1'),
			Log(level=LogLevel.WARNING, type=LogType.ENTITY, msg='msg2'),
			Log(level=LogLevel.ERROR, type=LogType.ELIST, msg='msg3')
		])

	def test_log_call(self):
		self.assertEqual(self.entity._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})")
		])
		self.entity.log_call(self.test_log_call, kwarg0='kwarg0', kwarg1=123)
		self.assertEqual(self.entity._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="test_log_call(kwarg0='kwarg0', kwarg1=123)")
		])

	def test_log_debug(self):
		self.entity.log_debug(type=LogType.ENTITY, msg='msg0')
		self.entity.log_debug(type=LogType.ELIST, msg='msg1')

		self.assertEqual(self.entity._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg='msg0'),
			Log(level=LogLevel.DEBUG, type=LogType.ELIST, msg='msg1'),
		])

	def test_log_info(self):
		self.entity.log_info(type=LogType.ENTITY, msg='msg0')
		self.entity.log_info(type=LogType.ELIST, msg='msg1')

		self.assertEqual(self.entity._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.INFO, type=LogType.ENTITY, msg='msg0'),
			Log(level=LogLevel.INFO, type=LogType.ELIST, msg='msg1'),
		])

	def test_log_warning(self):
		self.entity.log_warning(type=LogType.ENTITY, msg='msg0')
		self.entity.log_warning(type=LogType.ELIST, msg='msg1')

		self.assertEqual(self.entity._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.WARNING, type=LogType.ENTITY, msg='msg0'),
			Log(level=LogLevel.WARNING, type=LogType.ELIST, msg='msg1'),
		])

	def test_log_error(self):
		self.entity.log_error(type=LogType.ENTITY, msg='msg0')
		self.entity.log_error(type=LogType.ELIST, msg='msg1')

		self.assertEqual(self.entity._p_logs, [
			Log(level=LogLevel.DEBUG, type=LogType.ENTITY, msg="__init__(a='a', b='b', c=[1, 2, 3], d={'a': 'a', 'b': 1})"),
			Log(level=LogLevel.ERROR, type=LogType.ENTITY, msg='msg0'),
			Log(level=LogLevel.ERROR, type=LogType.ELIST, msg='msg1'),
		])


if __name__ == '__main__':
	unittest.main()
