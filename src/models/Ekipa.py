from typing import Optional

from sqlmodel import Field, SQLModel

from src.models.Oddelek import Oddelek_Tip


class Ekipa(SQLModel, table=True):
	id: int = Field(primary_key=True)

	# POVEZAVE
	ime: str
	opis: str
	tip: Oddelek_Tip
	oddelek: int = Field(foreign_key="oddelek.id")
