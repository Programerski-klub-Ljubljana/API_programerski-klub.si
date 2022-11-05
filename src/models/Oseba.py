from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Oseba(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)
	ime: str
	priimek: str
	email: str
	telefon: str
	vpisan: datetime = Field(default_factory=datetime.utcnow, nullable=False)
