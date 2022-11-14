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
		self.j = PersistentList([1, 2, 3])
		self.k = []
		self.l = {}
		self.n = PersistentList()
		self.o = c



json_object = Node(c=[Node(c=Node(c=[]))])
json = {
	'a': None,
	'b': True,
	'c': 1,
	'd': 1.2,
	'e': 'abc',
	'f': [None, True, 1, 1.2, 'asdf', [1, 2, 3], {'a': 1, 'b': 2}],
	'g': {'a': None, 'b': True, 'c': 1, 'd': 1.2, 'e': 'asdf', 'f': [1, 2, 3], 'g': {'a': 1, 'b': 2}},
	'j': [1, 2, 3],
	'k': [],
	'l': {},
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
			'j': [1, 2, 3],
			'k': [],
			'l': {},
			'n': [],
			'o': {
				'a': None,
				'b': True,
				'c': 1,
				'd': 1.2,
				'e': 'abc',
				'f': [None, True, 1, 1.2, 'asdf', [1, 2, 3], {'a': 1, 'b': 2}],
				'g': {'a': None, 'b': True, 'c': 1, 'd': 1.2, 'e': 'asdf', 'f': [1, 2, 3], 'g': {'a': 1, 'b': 2}},
				'j': [1, 2, 3],
				'k': [],
				'l': {},
				'n': [],
				'o': [],
			},
		}]
}


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
		self.assertEqual(json_object, utils.object_path(json_object, '/'))
		self.assertEqual(json_object, utils.object_path(json_object))
		self.assertEqual(json_object, utils.object_path(json_object, ''))

		def test(obj, path):
			self.assertEqual(obj, utils.object_path(json_object, path))
			if isinstance(obj, list):
				return True
			self.assertEqual(obj.j, utils.object_path(json_object, f'{path}/j'))
			self.assertEqual(obj.f[3], utils.object_path(json_object, f'{path}/f/3'))
			self.assertEqual(obj.g['d'], utils.object_path(json_object, f'{path}/g/d'))
			self.assertEqual(obj.j[-1], utils.object_path(json_object, f'{path}/j/-1'))
			self.assertEqual(obj.k, utils.object_path(json_object, f'{path}/k'))
			self.assertEqual(obj.l, utils.object_path(json_object, f'{path}/l'))
			self.assertEqual(obj.n, utils.object_path(json_object, f'{path}/n'))
			self.assertEqual(obj.o, utils.object_path(json_object, f'{path}/o'))
			return True

		self.assertTrue(test(json_object, ''))
		self.assertTrue(test(json_object.o, '/o'))
		self.assertTrue(test(json_object.o[0], '/o/0/'))
		self.assertTrue(test(json_object.o[0].o, '/o/0/o'))

	def test_object_json(self):
		self.assertEqual(utils.object_json([json_object, json_object], max_depth=10), [json, json])


if __name__ == '__main__':
	unittest.main()
