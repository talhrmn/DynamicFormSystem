from typing import List

from pydantic import BaseModel, Field


class SubmissionsDataResponse(BaseModel):
    """Response model for all submissions."""
    submissions: List[dict] = Field(description="List of all form submissions")
    total: int = Field(description="Total number of submissions")


class SubmissionsFormResponse(BaseModel):
    submissions: list[dict]
    page: int
    page_size: int
    pages: list[int]
    total: int
    total_pages: int
    columns: list[dict]
    filters_applied: dict
    sort_by: str
    sort_desc: bool
    filter_options: dict


class FieldStats(BaseModel):
    name: str
    type: str
    non_null_count: int
    unique_count: int


class StatsResponse(BaseModel):
    total_fields: int
    fields: List[FieldStats]


class DuplicateGroup(BaseModel):
    fields: dict
    count: int


class DuplicatesResponse(BaseModel):
    total_groups: int
    duplicates: List[DuplicateGroup]
