from typing import Any, Dict, List

from pydantic import BaseModel

from app.schemas.data.submissions import FieldStats


class AnalyticsResponse(BaseModel):
    total_submissions: int
    duplicates: List[Dict[str, Any]]
    field_stats: List[FieldStats]
