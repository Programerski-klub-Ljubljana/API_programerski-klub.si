import logging
from dataclasses import dataclass
from enum import auto, Enum

from core.cutils import list_field
from core.domain.arhitektura_kluba import Oseba
from core.services.db_service import DbService
from core.use_cases._usecase import UseCase
from core.use_cases.validation_cases import Poslji_test_ki_preveri_zeljo_za_koncno_izclanitev

log = logging.getLogger(__name__)


class TipPrekinitveIzpisa(str, Enum):
	NE_OBSTAJA = auto()
	NI_VPISAN = auto()


@dataclass
class StatusIzpisa:
	clan: Oseba | None = None
	razlogi_prekinitve: list[TipPrekinitveIzpisa] = list_field()


@dataclass
class Zacni_izclanitveni_postopek(UseCase):
	db: DbService
	validate_izpis_request: Poslji_test_ki_preveri_zeljo_za_koncno_izclanitev

	async def exe(self, ime: str, priimek: str, email: str, razlog: str) -> StatusIzpisa:
		# * POISCI CLANA V PODATKOVNI BAZI
		# ! ALI MORA BITI KONTAKT POTRJEN DA UPORABNIK GRE STRAN IZ KLUBA (NAJBRS DA NE) SAMO MORA POTRDITI POTDRITVENO KODO!
		# * PREVERI ALI JE EMAIL POTRJEN IZ STRANI UPORABNIKA
		# * SEAKTIVIRAJ SUBSCRIPTION PAYMENT CUSTOMERJA
		# * DODAJ NOV IZPIS CLANA
		# * IZPISI GA IZ ORGANIZACIJE

		# TUKAJ NIC NE SPREMINJAJ V BAZI SPREMENI SELE KO UPORABNIK POTRDI NA EMAILU DA JE UPORABNIK!
		izpis = StatusIzpisa()

		# POISCI OSEBO PO POTRJENEM KONTAKTU
		for oseba in self.db.oseba_find(data=email):

			# ALI SE IME UJEMA...
			if oseba.ime == ime and oseba.priimek == priimek:
				izpis.clan = oseba
				if not oseba.vpisan:
					izpis.razlogi_prekinitve.append(TipPrekinitveIzpisa.NI_VPISAN)

		if izpis.clan is None:
			izpis.razlogi_prekinitve.append(TipPrekinitveIzpisa.NE_OBSTAJA)

		if len(izpis.razlogi_prekinitve) == 0:
			await self.validate_izpis_request.exe(oseba=izpis.clan)

		return izpis
