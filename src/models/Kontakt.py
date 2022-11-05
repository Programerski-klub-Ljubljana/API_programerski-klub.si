from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Kontakt(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)
	ime: str
	priimek: str
	email: str
	telefon: str
	ustvarjen: datetime = Field(default_factory=datetime.utcnow, nullable=False)
