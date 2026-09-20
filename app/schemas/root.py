"""Root API information response schema."""

from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    name: str = Field(examples=["AI Personal Assistant"])
    version: str = Field(examples=["0.1.0"])
    environment: str = Field(examples=["development"])
    docs: str = Field(examples=["/docs"])
