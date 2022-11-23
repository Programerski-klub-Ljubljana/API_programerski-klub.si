import unittest

from app import APP
from core.services.db_service import DbService
from core.use_cases.forms_vpis import Forms_vpis


class Test_forms_vpis(unittest.TestCase):
	def setUpClass(cls) -> None:
		APP.init(seed=True)




if __name__ == '__main__':
	unittest.main()
