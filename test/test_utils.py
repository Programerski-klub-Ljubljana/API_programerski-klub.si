import unittest
from datetime import datetime
from pathlib import Path

from persistent.list import PersistentList

from core import utils


class Node:
	def __init__(self, c):
		self.i = 123
		self.f = 12.34
		self.s = 'abc'
		self.t = (1, 'a')
		self.d = {'a': 'b', 'c': 'd'}
		self.b = True
		self.c = c


class test_validate(unittest.TestCase):

	def setUp(self) -> None:
		pass

	def test_root_path(self):
		result = utils.root_path('api')
		self.assertEqual(result, Path('../api').resolve().absolute())

	def test_age(self):
		today = datetime.utcnow()
		self.assertEqual(12.5027, round(utils.age(today.year - 12, today.month - 6, today.day - 1), 4))

	def test_is_iterable(self):
		self.assertTrue(utils.is_iterable([1, 2, 3]))
		self.assertTrue(utils.is_iterable(PersistentList([1, 2])))
		self.assertTrue(utils.is_iterable((1,)))

		self.assertFalse(utils.is_iterable(123))
		self.assertFalse(utils.is_iterable("asdf"))
		self.assertFalse(utils.is_iterable(Path()))

	def test_is_object(self):
		self.assertTrue(Path())
		self.assertTrue({1: 3})
		self.assertTrue(123)

		# WTF ???
		self.assertFalse(0)
		self.assertFalse({})
		self.assertTrue(1)

	def test_object_path(self):
		n = Node(c=[
			Node(c=Node(c=[
				Node(c=Node([]))
			])),
			Node([])
		])

		# TESTING EDGE CASES
		self.assertEqual(n, utils.object_path(n, path='/'))
		self.assertEqual(n, utils.object_path(n))
		self.assertEqual(n, utils.object_path(n, path=''))

		# TESTING ALL CASES
		self.assertEqual(n.c, utils.object_path(n, path='/c'))
		self.assertEqual(n.i, utils.object_path(n, path='/i'))
		self.assertEqual(n.t[0], utils.object_path(n, path='/t/0'))
		self.assertEqual(n.t[1], utils.object_path(n, path='/t/1'))
		self.assertEqual(n.d['c'], utils.object_path(n, path='/d/c'))
		self.assertEqual(n.c[0], utils.object_path(n, path='/c/0'))
		self.assertEqual(n.c[1], utils.object_path(n, path='/c/1'))
		self.assertEqual(n.c[1].c, utils.object_path(n, path='/c/1/c'))

	def test_object_json(self):
		n = Node(c=[
			Node(c=Node(c=[])),
			Node([])
		])
		self.assertEqual(utils.object_json(n), {
			'i': 123,
			'f': 12.34,
			's': 'abc',
			't': (1, 'a'),
			'd': {'a': 'b', 'c': 'd'},
			'b': True,
			'c': [{
				'i': 123,
				'f': 12.34,
				's': 'abc',
				't': (1, 'a'),
				'd': {'a': 'b', 'c': 'd'},
				'b': True,
				'c': {
					'i': 123,
					'f': 12.34,
					's': 'abc',
					't': (1, 'a'),
					'd': {'a': 'b', 'c': 'd'},
					'b': True,
					'c': []
				}

			}, {
				'i': 123,
				'f': 12.34,
				's': 'abc',
				't': (1, 'a'),
				'd': {'a': 'b', 'c': 'd'},
				'b': True,
				'c': []
			}]
		})


if __name__ == '__main__':
	unittest.main()
