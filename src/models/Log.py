from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Tip(str, Enum):
	VPIS = 'VPIS'
	IZPIS = 'IZPIS'
	KONTAKT = 'KONTAKT'


class Level(str, Enum):
	INFO = 'INFO'
	WARNING = 'WARNING'
	ERROR = 'ERROR'


class Service(str, Enum):
	EMAIL = 'EMAIL'
	DB = 'DB',
	API = 'API'


class Log(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)

	clan: Optional[int] = Field(default=None, foreign_key="clan.id")
	kontakt: Optional[int] = Field(default=None, foreign_key="kontakt.id")
	placilo: Optional[int] = Field(default=None, foreign_key="placilo.id")
	skrbnik: Optional[int] = Field(default=None, foreign_key="skrbnik.id")
	sporocilo: Optional[int] = Field(default=None, foreign_key="sporocilo.id")

	tip: Tip
	level: Level
	service: Service
	msg: str
