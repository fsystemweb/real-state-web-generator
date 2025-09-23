from typing import Optional
from pydantic import BaseModel

class Location(BaseModel):
    city: str
    neighborhood: Optional[str] = None

class Features(BaseModel):
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area_sqm: Optional[float] = None
    balcony: Optional[bool] = None
    parking: Optional[bool] = None
    elevator: Optional[bool] = None
    floor: Optional[int] = None
    year_built: Optional[int] = None

class PropertyData(BaseModel):
    title: str
    location: Location
    features: Features
    price: Optional[float] = None
    listing_type: str  # e.g., "sale" or "rent"
    language: str      # "en" or "pt"
