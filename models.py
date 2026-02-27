from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional

class URLDBModel(BaseModel):
    """
    Representation of a URL document in the database.
    Using BaseModel to structure the data properly before inserting into MongoDB.
    """
    original_url: str
    short_code: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    click_count: int = 0
