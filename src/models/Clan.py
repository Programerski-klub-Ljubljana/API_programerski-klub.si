from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel

class Oddelek(str, Enum):
	TRENERSKI = 'TRENERSKI'
	OSNOVNOSOLSKI = 'OSNOVNOSOLSKI'
	SREDNJESOLSKI = 'SREDNJESOLSKI'
	CLANSKI = 'CLANSKI'
	PREKVALIFIKACIJSKI = 'PREKVALIFIKACIJSKI'
	STUDENTSKI = 'STUDENTSKI'
	UPRAVNI = 'UPRAVNI'
	NADZORNISKI = 'NAZDZORNISKI'
	ZUNANJI = 'ZUNANJI' # Vsi ki so prisotni na dogodku vendar niso se clani.
	ZAPOSLITVENI = 'ZAPOSLITVENI'

class Clan(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)

	#INFO
	ime: str
	priimek: str
	rojen: datetime = Field(nullable=False)

	# KONTAKT
	email: Optional[str] = None
	telefon: Optional[str] = None

	# DATUMI
	oddelek: Oddelek
	vpisan: datetime = Field(default_factory=datetime.utcnow, nullable=False)
	izpisan: Optional[datetime] = Field(nullable=True)
	ustvarjen: datetime = Field(default_factory=datetime.utcnow, nullable=False)

	# POVEZAVE
	skrbnik: Optional[int] = Field(default=None, foreign_key="skrbnik.id")
