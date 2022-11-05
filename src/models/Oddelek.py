from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel

class Oddelek_Tip(str, Enum):
	TRENERSKI = 'TRENERSKI'
	OSNOVNOSOLSKI = 'OSNOVNOSOLSKI'
	SREDNJESOLSKI = 'SREDNJESOLSKI'
	CLANSKI = 'CLANSKI'
	PREKVALIFIKACIJSKI = 'PREKVALIFIKACIJSKI'
	STUDENTSKI = 'STUDENTSKI'
	UPRAVNI = 'UPRAVNI'
	NADZORNISKI = 'NAZDZORNISKI'
	ZUNANJI = 'ZUNANJI'  # Vsi ki so prisotni na dogodku vendar niso se clani.
	ZAPOSLITVENI = 'ZAPOSLITVENI'


class Oddelek(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)

	# POVEZAVE
	ime: str
	opis: str
	tip: Oddelek_Tip
