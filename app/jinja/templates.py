from pathlib import Path

from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "jinja/templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def format_field_value(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


templates.env.filters["format_value"] = format_field_value
