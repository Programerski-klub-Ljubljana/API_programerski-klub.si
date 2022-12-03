import logging
from dataclasses import dataclass
from enum import auto, Enum

from core.cutils import list_field
from core.domain.arhitektura_kluba import Oseba
from core.services.db_service import DbService
from core.use_cases._usecase import UseCase
from core.use_cases.validation_cases import Validate_izpis_request

log = logging.getLogger(__name__)


class TipPrekinitveIzpisa(str, Enum):
	NE_OBSTAJA = auto()
	NI_VPISAN = auto()


@dataclass
class StatusIzpisa:
	clan: Oseba | None = None
	razlogi_prekinitve: list[TipPrekinitveIzpisa] = list_field()


@dataclass
class Forms_izpis(UseCase):
	db: DbService
	validate_izpis_request: Validate_izpis_request

	async def invoke(self, ime: str, priimek: str, email: str, razlog: str) -> StatusIzpisa:
		kwargs = locals()
		del kwargs['self']

		# TUKAJ NIC NE SPREMINJAJ V BAZI SPREMENI SELE KO UPORABNIK POTRDI NA EMAILU DA JE UPORABNIK!
		izpis = StatusIzpisa()

		# POISCI OSEBO PO POTRJENEM KONTAKTU
		for oseba in self.db.oseba_find(kontakt_data=email):

			# ALI SE IME UJEMA...
			if oseba.ime == ime and oseba.priimek == priimek:
				izpis.clan = oseba
				if not oseba.vpisan:
					izpis.razlogi_prekinitve.append(TipPrekinitveIzpisa.NI_VPISAN)

		if izpis.clan is None:
			izpis.razlogi_prekinitve.append(TipPrekinitveIzpisa.NE_OBSTAJA)

		if len(izpis.razlogi_prekinitve) == 0:
			await self.validate_izpis_request.invoke(oseba=izpis.clan)

		return izpis
