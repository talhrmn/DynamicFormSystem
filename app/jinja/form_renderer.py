from datetime import date
from typing import Dict, Any, Optional, List

from app.common.schemas import FormSchema
from app.jinja.consts import FORM_ACTION_PATH, FORM_TITLE
from app.jinja.form_context import FormContext
from app.jinja.form_field import FormField


class FormRenderer:
    """
    Service for generating template context for dynamic forms.
    """

    @staticmethod
    def create_form_context(
            form_schema: FormSchema,
            values: Optional[Dict[str, Any]] = None,
            errors: Optional[Dict[str, str]] = None,
            form_title: str = FORM_TITLE,
            form_action: str = FORM_ACTION_PATH,
            success_message: Optional[str] = None,
    ) -> FormContext:
        """
        Build a FormContext from a FormSchema.
        Fields preserve the order from the schema dict.
        """
        values = values or {}
        errors = errors or {}

        fields: List[FormField] = []
        for field_name, field_schema in form_schema.fields.items():
            fields.append(
                FormField(
                    name=field_name,
                    field_schema=field_schema,
                    value=values.get(field_name),
                    error=errors.get(field_name),
                )
            )

        return FormContext(
            fields=fields,
            form_title=form_title,
            form_action=form_action,
            errors=errors,
            success_message=success_message,
        )

    @staticmethod
    def prepare_schema_preview(form_schema: FormSchema) -> Dict[str, Any]:
        """
        Prepare a simple preview of schema constraints for UI display.
        """
        fields_info = []
        for name, cfg in form_schema.fields.items():
            info = {
                "name": name,
                "type": cfg.type,
                "required": cfg.required,
                "constraints": [],
            }

            for attr in ("min_length", "max_length", "min", "max", "options", "pattern"):
                val = getattr(cfg, attr, None)
                if val is None:
                    continue
                if attr == "options":
                    info["constraints"].append(f"Options: {', '.join(val)}")
                elif attr == "pattern":
                    info["constraints"].append(f"Pattern: {val}")
                elif attr in ("min", "min_length"):
                    info["constraints"].append(f"Min {attr.replace('_', ' ')}: {val}")
                else:
                    info["constraints"].append(f"Max {attr.replace('_', ' ')}: {val}")

            fields_info.append(info)

        return {
            "fields": fields_info,
            "field_count": len(fields_info),
            "required_count": len([f for f in fields_info if f["required"]]),
        }

    @staticmethod
    def create_success_context(
            submission_id: str,
            submitted_data: Dict[str, Any],
            form_title: str = "Submission Successful",
    ) -> Dict[str, Any]:
        """Create render context for the success page."""
        return {
            "title": form_title,
            "submission_id": submission_id,
            "submitted_data": submitted_data,
            "timestamp": date.today().isoformat(),
        }
