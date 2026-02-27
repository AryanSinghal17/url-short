from pydantic import BaseModel, HttpUrl
from datetime import datetime

class URLCreate(BaseModel):
    """Schema for the creating a URL request payload"""
    original_url: str  # Note: Can use HttpUrl, but str allows broader testing on localhost urls.

class URLResponse(BaseModel):
    """Schema for returning URL data"""
    original_url: str
    short_code: str
    created_at: datetime
    click_count: int

    class Config:
        from_attributes = True
