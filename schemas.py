"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Ahmedabad x Anime Design Assistant Schemas

FormatType = Literal["Sticker", "Poster", "Badge"]
ArtStyle = Literal["Anime", "Manga", "Chibi", "Realistic"]
ColorPalette = Literal["Vibrant", "Pastel", "Monochrome"]

class Customization(BaseModel):
    pose_change: Optional[str] = Field(None, description="Pose modifications, e.g., facing left")
    background: Optional[str] = Field(None, description="Background description, e.g., Ahmedabad street scene with Fafda/Jalebi stall")
    composition: Optional[str] = Field(None, description="Composition adjustments, e.g., move to right side of frame")
    narrative: Optional[str] = Field(None, description="Narrative element, e.g., character eating local food")

class StyleVariant(BaseModel):
    format: FormatType
    art_style: ArtStyle
    color_palette: ColorPalette
    label: Optional[str] = None
    asset_url: Optional[str] = None

class DesignSession(BaseModel):
    title: Optional[str] = Field(None, description="Human-friendly session title")
    reference_images: List[str] = Field(default_factory=list, description="List of uploaded reference image URLs")
    extracted_features: Dict = Field(default_factory=dict, description="Auto-extracted character features from references")
    customization: Optional[Customization] = None
    variations: List[StyleVariant] = Field(default_factory=list)
    status: Literal["created", "customized", "rendered"] = "created"

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
