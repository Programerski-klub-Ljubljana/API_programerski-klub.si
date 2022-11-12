from core.services.db_service import DbService


class ZoDB(DbService):
	def save_clan(self, clan):
		print('save clan')
