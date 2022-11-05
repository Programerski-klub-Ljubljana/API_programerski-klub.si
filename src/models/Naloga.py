from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel

class Tezavnost(str, Enum):
	PREPROSTA = 'PREPROSTA'
	LAHKA = 'LAHKA'
	NORMALNA = 'NORMALNA'
	TEZKA = 'TEZKA'
	NEMOGOCA = 'NEMOGOCA'


class Naloga(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)
	stevilo_algoritmov: int
	tezavnost_algoritmov: Tezavnost
	tezavnost_struktur: Tezavnost
	koda: Optional[str]
