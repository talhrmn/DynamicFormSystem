from typing import List, Optional, Dict

from app.jinja.consts import FORM_ACTION_PATH, FORM_TITLE
from app.jinja.form_field import FormField


class FormContext:
    """
    Context object containing all data needed to render a form.

    This provides a clean interface for templates.
    """

    def __init__(
            self,
            fields: List[FormField],
            form_title: str = FORM_TITLE,
            form_action: str = FORM_ACTION_PATH,
            form_method: str = "POST",
            submit_text: str = "Submit",
            errors: Optional[Dict[str, str]] = None,
            success_message: Optional[str] = None,
            show_required_indicator: bool = True,
    ):
        """
        Initialize form render context.

        Args:
            fields: List of FormField objects
            form_title: Title to display above form
            form_action: Form action URL
            form_method: HTTP method (GET or POST)
            submit_text: Text for submit button
            errors: Dictionary of field errors
            success_message: Success message to display
            show_required_indicator: Whether to show "* Required" indicator
        """
        self.fields = fields
        self.form_title = form_title
        self.form_action = form_action
        self.form_method = form_method
        self.submit_text = submit_text
        self.errors = errors or {}
        self.success_message = success_message
        self.show_required_indicator = show_required_indicator

        # Categorize fields for convenience in templates
        self.required_fields = [f for f in fields if f.required]
        self.optional_fields = [f for f in fields if not f.required]
        self.has_errors = bool(self.errors) or any(bool(f.error) for f in fields)
