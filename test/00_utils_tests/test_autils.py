import json
import unittest

from fastapi import APIRouter

from api import autils
from app import CONST


class test_autils(unittest.TestCase):
	def test_router(self):
		router = autils.router(__name__)
		self.assertIsInstance(router, APIRouter)
		self.assertEqual(router.prefix, f'/test_autils')
		self.assertListEqual(router.tags, ['test_autils'])

	def test_openapi(self):
		data = autils.openapi({
			"info": {},
			"paths": {
				"/route0": {
					"get": {
						"tags": ["DB"],
						"summary": "Get Table Data",
						"operationId": "gettabledata",
					}
				},
			},
			"components": {
				"schemas": {
					"Body_gettabledata": {
					},
				},
			}
		})
		self.assertEqual(json.dumps(data, indent=4), json.dumps({
			"info": {
				'x-logo': {'url': CONST.logo}  # ADDS LOGO OF COMPANY
			},
			"paths": {
				"/route0": {
					"get": {
						"tags": ["DB"],
						"summary": "Get Table Data",
						"operationId": "get_table_data"  # FORMAT OPERATION ID
					}
				}
			},
			"components": {
				"schemas": {
					"Body_gettabledata": {  # THIS MUST BE THE SAME OPENAPI FUCCKERY
						"title": "Db get table data"  # CREATE TITLE
					}
				}
			}
		}, indent=4))


if __name__ == '__main__':
	unittest.main()
