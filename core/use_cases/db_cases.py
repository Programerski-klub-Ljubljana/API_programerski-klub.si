from dataclasses import dataclass
from typing import Any

from autologging import traced

from core import cutils
from core.services.db_service import DbService
from core.use_cases._usecase import UseCase


@traced
@dataclass
class Vrni_vsebino_baze(UseCase):
	db: DbService

	def exe(self, table: str, path: str = None, page: int = 0, per_page: int = 10, max_depth: int = 3, max_width: int = 10) -> Any:
		with self.db.transaction() as root:
			result = cutils.object_path(getattr(root, table), path)
			start = per_page * page
			end = per_page * (page + 1)
			result = result[start:end] if cutils.is_iterable(result) else result
			return cutils.object_json(result, max_depth=max_depth, max_width=max_width)


@traced
@dataclass
class Db_check_consistency(UseCase):
	db: DbService

	def exe(self) -> Any:  # TODO: ensure that only valid originals are in db!!!
		# Todo: check for duplicates in tables
		# Todo: check for consistency for joining elements
		# TODO: clean kontacts that are unvalidated for more than 2 days.
		# TODO: ce je vpisan mora biti tudi clan
		# TODO: Only one kontakt can have one number!
		# TODO: Test if underage is finaly 18 (setup things in stripe)
		# TODO: Check consistency with db and stripe api.
		pass
