import logging
from dataclasses import dataclass

from core.cutils import list_field
from core.domain.arhitektura_kluba import Oseba
from core.services.db_service import DbService
from core.use_cases._usecase import UseCase
from core.use_cases.forms_vpis import TipProblema

log = logging.getLogger(__name__)


class StatusIzpisa:
	clan: Oseba | None = None
	skrbnik: Oseba | None = None
	razlogi_prekinitve: list[TipProblema] = list_field()


@dataclass
class Forms_izpis(UseCase):
	db: DbService

	async def invoke(self, ime: str, priimek: str, email: str, razlog: str) -> StatusIzpisa:
		pass
