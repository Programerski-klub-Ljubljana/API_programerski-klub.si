from dataclasses import dataclass
from typing import Any

from autologging import traced

from core import cutils
from core.domain.arhitektura_kluba import TipOsebe, Oseba
from core.services.db_service import DbService
from core.use_cases._usecase import UseCase


@traced
@dataclass
class Db_path(UseCase):
	db: DbService

	def invoke(self, table: str, path: str = None, page: int = 0, per_page: int = 10, max_depth: int = 3, max_width: int = 10) -> Any:
		with self.db.transaction() as root:
			result = cutils.object_path(getattr(root, table), path)
			start = per_page * page
			end = per_page * (page + 1)
			result = result[start:end] if cutils.is_iterable(result) else result
			return cutils.object_json(result, max_depth=max_depth, max_width=max_width)


@traced
@dataclass
class Db_merge_oseba(UseCase):
	db: DbService

	def invoke(self, oseba, as_type: TipOsebe) -> Oseba:
		# PREVERI MOZNO DUPLIKACIJO PODATKOV!
		with self.db.transaction(note=f'Merge {oseba} if already exists') as root:
			for old_oseba in root.oseba:

				# LOGIKA CE CLAN ZE OBSTAJA...
				if old_oseba == oseba:

					# MERGING OLD WITH NEW
					old_oseba.dodaj_kontakte(*oseba.kontakti)  # MERGAJ SVEZE KONTAKTE CE OBSTAJAJO
					old_oseba.dodaj_tip_osebe(*oseba.statusi)  # MERGAJ STATUSE!
					oseba = old_oseba  # UPORABI STARO OSEBO KI ZE OBSTAJA DA PREPRECIS DUPLIKATE V BAZI

					if not oseba.vpisan:
						oseba.nov_vpis()

		return oseba


@traced
@dataclass
class Db_check_consistency(UseCase):
	db: DbService

	def invoke(self) -> Any:  # TODO: ensure that only valid originals are in db!!!
		# Todo: check for duplicates in tables
		# Todo: check for consistency for joining elements
		# TODO: clean kontacts that are unvalidated for more than 2 days.
		# TODO: ce je vpisan mora biti tudi clan
		# TODO: Only one kontakt can have one number!
		pass
