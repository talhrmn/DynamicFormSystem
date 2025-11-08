from typing import Optional, Any, Dict, List

from app.common.enums import SupportedFieldTypes
from app.common.schemas import FieldSchema


class FormField:
    """
    Represents a single form field with rendering metadata.
    """

    def __init__(
            self,
            name: str,
            field_schema: FieldSchema,
            value: Optional[Any] = None,
            error: Optional[str] = None,
    ):
        self.name = name
        self.label = self._generate_label(name)
        self.type = field_schema.type
        self.required = bool(field_schema.required)
        self.value = value
        self.error = error

        # Schema-driven attributes
        self.min_length = getattr(field_schema, "min_length", None)
        self.max_length = getattr(field_schema, "max_length", None)
        self.min_value = getattr(field_schema, "min", None)
        self.max_value = getattr(field_schema, "max", None)
        self.options = getattr(field_schema, "options", None)
        self.pattern = getattr(field_schema, "pattern", None)

        self.html_type = self._get_html_input_type()
        self.css_classes = self._generate_css_classes()
        self.html_attrs = self._generate_html_attributes()

    @staticmethod
    def _generate_label(field_name: str) -> str:
        """Generate a human-readable label from field name."""
        return field_name.replace("_", " ").title()

    def _get_html_input_type(self) -> str:
        """Map logical field type to HTML input type."""
        type_mapping = {
            SupportedFieldTypes.TEXT: "text",
            SupportedFieldTypes.STRING: "text",
            SupportedFieldTypes.EMAIL: "email",
            SupportedFieldTypes.PASSWORD: "password",
            SupportedFieldTypes.DATE: "date",
            SupportedFieldTypes.NUMBER: "number",
            SupportedFieldTypes.DROPDOWN: "select",
        }
        return type_mapping.get(self.type, "text")

    def _generate_html_attributes(self) -> Dict[str, Any]:
        """Generate HTML attributes for the field element."""
        attrs: Dict[str, Any] = {
            "id": f"field_{self.name}",
            "name": self.name,
            "class": " ".join(self.css_classes),
        }

        if self.required:
            attrs["required"] = True

        # String-like constraints
        if self.type in (SupportedFieldTypes.STRING, SupportedFieldTypes.TEXT):
            if self.min_length:
                attrs["minlength"] = self.min_length
            if self.max_length:
                attrs["maxlength"] = self.max_length
            if self.pattern:
                attrs["pattern"] = self.pattern

        # Number constraints
        if self.type == SupportedFieldTypes.NUMBER:
            if self.min_value is not None:
                attrs["min"] = self.min_value
            if self.max_value is not None:
                attrs["max"] = self.max_value
            attrs["step"] = "any"

        # Password constraints (same as string but explicit)
        if self.type == SupportedFieldTypes.PASSWORD:
            if self.min_length:
                attrs["minlength"] = self.min_length
            if self.max_length:
                attrs["maxlength"] = self.max_length

        # Dropdown doesn't need input attrs beyond options — template will render <select>

        return attrs

    def _generate_css_classes(self) -> List[str]:
        """Return a list of CSS classes for the field."""
        classes = ["form-control"]
        if self.error:
            classes.append("is-invalid")
        if self.required:
            classes.append("required")
        classes.append(f"field-type-{self.type}")
        return classes

    def get_attributes_string(self) -> str:
        """
        Convert html_attrs dict to a string for template rendering.
        Example: id="field_name" required
        """
        parts: List[str] = []
        for key, value in self.html_attrs.items():
            if isinstance(value, bool) and value:
                parts.append(key)
            else:
                parts.append(f'{key}="{value}"')
        return " ".join(parts)
