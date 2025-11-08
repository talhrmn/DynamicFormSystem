from typing import List

from pydantic import BaseModel, Field


class SubmissionsDataResponse(BaseModel):
    """Response model for all submissions."""
    submissions: List[dict] = Field(description="List of all form submissions")
    total: int = Field(description="Total number of submissions")
