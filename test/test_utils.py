import unittest
from datetime import datetime
from pathlib import Path

from persistent.list import PersistentList

from core import utils


class Node:
	def __init__(self, c):
		# 15
		self.a = None
		self.b = True
		self.c = 1
		self.d = 1.2
		self.e = "abc"
		self.f = [None, True, 1, 1.2, "asdf", [1, 2, 3], {'a': 1, 'b': 2}]
		self.g = {'a': None, 'b': True, 'c': 1, 'd': 1.2, 'e': 'asdf', 'f': [1, 2, 3], 'g': {'a': 1, 'b': 2}}
		self.h = (None, True, 1, 1.2, "asdf")
		self.i = {None, True, 1, 1.2, "asdf"}
		self.j = PersistentList([1, 2, 3])
		self.k = []
		self.l = {}
		self.m = ()
		self.n = PersistentList()
		self.o = c


class test_validate(unittest.TestCase):

	def setUp(self) -> None:
		self.dict = [{'key': 1, 'key2': 'asdf'}, {}]
		self.iterable = [[1, "asdf", True], (1, "asdf", True), {1, 2, 3}, PersistentList()]
		self.values = [None, True, 1, 1.2, "asdf"]
		self.objects = [Node(c=[])]

	def test_root_path(self):
		result = utils.root_path('api')
		self.assertEqual(result, Path('../api').resolve().absolute())

	def test_age(self):
		today = datetime.utcnow()
		self.assertEqual(12.5027, round(utils.age(today.year - 12, today.month - 6, today.day - 1), 4))

	def test_is_iterable(self):
		for ele in self.iterable:
			self.assertTrue(utils.is_iterable(ele), ele)

		for ele in self.dict + self.values + self.objects:
			self.assertFalse(utils.is_iterable(ele), ele)

	def test_is_mappable(self):
		for ele in self.dict:
			self.assertTrue(utils.is_mappable(ele), ele)

		for ele in self.iterable + self.values + self.objects:
			self.assertFalse(utils.is_mappable(ele), ele)

	def test_is_object(self):
		for ele in self.objects:
			self.assertTrue(utils.is_object(ele), ele)

		for ele in self.dict + self.iterable + self.values:
			self.assertFalse(utils.is_object(ele), ele)

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
		n = Node(c=[Node(c=Node(c=[])), ])
		json = {
			'a': None,
			'b': True,
			'c': 1,
			'd': 1.2,
			'e': 'abc',
			'f': [None, True, 1, 1.2, 'asdf', [1, 2, 3], {'a': 1, 'b': 2}],
			'g': {'a': None, 'b': True, 'c': 1, 'd': 1.2, 'e': 'asdf', 'f': [1, 2, 3], 'g': {'a': 1, 'b': 2}},
			'h': [None, True, 1, 1.2, 'asdf'],
			'i': list({1.2, True, 'asdf', None}),
			'j': [1, 2, 3],
			'k': [],
			'l': {},
			'm': [],
			'n': [],
			'o': [
				{
					'a': None,
					'b': True,
					'c': 1,
					'd': 1.2,
					'e': 'abc',
					'f': [None, True, 1, 1.2, 'asdf', [1, 2, 3], {'a': 1, 'b': 2}],
					'g': {'a': None, 'b': True, 'c': 1, 'd': 1.2, 'e': 'asdf', 'f': [1, 2, 3], 'g': {'a': 1, 'b': 2}},
					'h': [None, True, 1, 1.2, 'asdf'],
					'i': list({1.2, True, 'asdf', None}),
					'j': [1, 2, 3],
					'k': [],
					'l': {},
					'm': [],
					'n': [],
					'o': {
						'a': None,
						'b': True,
						'c': 1,
						'd': 1.2,
						'e': 'abc',
						'f': [None, True, 1, 1.2, 'asdf', [1, 2, 3], {'a': 1, 'b': 2}],
						'g': {'a': None, 'b': True, 'c': 1, 'd': 1.2, 'e': 'asdf', 'f': [1, 2, 3], 'g': {'a': 1, 'b': 2}},
						'h': [None, True, 1, 1.2, 'asdf'],
						'i': list({1.2, True, 'asdf', None}),
						'j': [1, 2, 3],
						'k': [],
						'l': {},
						'm': [],
						'n': [],
						'o': [],
					},
				}],
		}
		self.assertEqual(utils.object_json([n, n], max_depth=10), [json, json])


if __name__ == '__main__':
	unittest.main()
