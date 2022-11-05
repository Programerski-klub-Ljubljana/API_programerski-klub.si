from typing import Optional

from sqlmodel import Field, SQLModel

from src.models.Clan import Oddelek


class Ekipa(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)

	# POVEZAVE
	ime: str
	opis: str
	oddelek: Oddelek
	trener: Optional[int] = Field(default=None, foreign_key="clan.id")
	asistent: Optional[int] = Field(default=None, foreign_key="clan.id")
	odgovorni: Optional[int] = Field(default=None, foreign_key="clan.id")
