from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

from app.common.enums import SupportedFieldTypes


class FieldSchema(BaseModel):
    """Schema definition for a single form field."""
    type: SupportedFieldTypes
    required: bool = False
    min_length: Optional[int] = Field(None, alias="minLength", ge=0)
    max_length: Optional[int] = Field(None, alias="maxLength", ge=0)
    min: Optional[float] = Field(None, ge=0)
    max: Optional[float] = None
    options: Optional[List[str]] = None
    pattern: Optional[str] = None

    class Config:
        populate_by_name = True
        use_enum_values = True


class FormSchema(BaseModel):
    """Complete form schema containing all field definitions."""
    fields: Dict[str, FieldSchema]

    @classmethod
    def from_dict(cls, schema: Dict[str, Any]):
        """
        Create FormSchema from a dictionary.
        """
        fields = {
            field_name: FieldSchema(**field_config)
            for field_name, field_config in schema.items()
        }
        return cls(fields=fields)

    def get_required_fields(self) -> List[str]:
        """Get list of required field names."""
        return [
            name for name, config in self.fields.items()
            if config.required
        ]

    def get_field_names(self) -> List[str]:
        """Get list of all field names."""
        return list(self.fields.keys())
