from dataclasses import dataclass
from typing import Any

from core import cutils
from core.services.db_service import DbService


@dataclass
class DbUseCase:
	dbService: DbService


class Db_path(DbUseCase):
	def invoke(self, table: str, path: str = None, page: int = 0, per_page: int = 10, max_depth: int = 3, max_width: int = 10) -> Any:
		with self.dbService.transaction() as root:
			result = cutils.object_path(getattr(root, table), path)
			start = per_page * page
			end = per_page * (page + 1)
			result = result[start:end] if cutils.is_iterable(result) else result
			return cutils.object_json(result, max_depth=max_depth, max_width=max_width)
