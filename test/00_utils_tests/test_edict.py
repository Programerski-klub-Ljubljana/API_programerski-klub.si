import unittest
from dataclasses import dataclass

from core.domain._entity import Entity, Log, Edict
from core.domain._enums import LogLevel, LogType


@dataclass
class E(Entity):
	value: int


class test_Edict(unittest.TestCase):
	def setUp(cls) -> None:
		cls.edict = Edict(data={'a': E(1), 'b': E(2), 'c': E(3)})

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


if __name__ == '__main__':
	unittest.main()
