from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel

from src.models.Clan import Oddelek

class Tip(str, Enum):
	TEKMA = 'TEKMA'
	TRENING = 'TRENING'
	SRECANJE = 'SRECANJE'
	UPRAVNI_ODBOR = "UPRAVNI_ODBOR"


class Lokacija(str, Enum):
	GITHUB = 'GITHUB'
	OSNOVNA_SOLA = 'OSNOVNA_SOLA'
	SREDNJA_SOLA = 'SREDNJA_SOLA'
	FAKULTETA = 'FAKULTETA'


class Dogodek(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)

	# POVEZAVE
	ime: str
	opis: str
	trajanje: float
	lokacija: Lokacija
	oddelek: Oddelek
	zacetek: datetime = Field(nullable=False)
	konec: datetime = Field(nullable=False)
	registriran: datetime = Field(default_factory=datetime.utcnow, nullable=False)
