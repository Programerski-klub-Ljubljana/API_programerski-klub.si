from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Transakcija_Tip(str, Enum):
	CLANARINA = 'CLANARINA'
	PLACA = 'PLACA'
	STROSKI = 'STROSKI'
	OPREMA = 'OPREMA'


class Transakcija(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)
	tip: Transakcija_Tip
	znesek: float
	placano: float
	ustvarjen: datetime = Field(default_factory=datetime.utcnow, nullable=False)
	rok: datetime = Field(default_factory=datetime.utcnow, nullable=False)
