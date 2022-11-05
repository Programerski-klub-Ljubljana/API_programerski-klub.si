from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel

class Tip(str, Enum):
	EMAIL = 'ZAPOSLOVANJE'
	SMS = 'SMS'

class Objava(SQLModel, table=True):
	id: Optional[int] = Field(primary_key=True)
	tip: Tip
	template: str
	body: str
	ustvarjena: datetime = Field(default_factory=datetime.utcnow, nullable=False)
