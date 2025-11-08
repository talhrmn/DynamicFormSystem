from typing import Dict, Any, Optional, Type

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.logger import get_logger
from app.common.schemas import FormSchema
from app.core.config import get_settings
from app.core.system import get_system_manager
from app.jinja.consts import FORM_ACTION_PATH, FORM_TITLE
from app.jinja.form_renderer import FormRenderer
from app.repositories.submissions_repo import SubmissionsRepo

logger = get_logger()
settings = get_settings()


class FormService:
    """
    Service layer for manging forms.
    """

    def __init__(self, table_model: Type, session: AsyncSession):
        self.system_manager = get_system_manager()
        self.repo = SubmissionsRepo(table_model, session)

    # --- Rendering helpers (UI layer kept in renderer) ---------------------

    @staticmethod
    async def get_form_context(
            form_schema: FormSchema,
            values: Optional[Dict[str, Any]] = None,
            errors: Optional[Dict[str, str]] = None,
            form_title: str = FORM_TITLE,
            form_action: str = FORM_ACTION_PATH,
            success_message: Optional[str] = None,
    ):
        """
        Return a context ready for template rendering using FormRenderer.
        """
        return FormRenderer.create_form_context(
            form_schema=form_schema,
            values=values,
            errors=errors,
            form_title=form_title,
            form_action=form_action,
            success_message=success_message,
        )

    @staticmethod
    async def get_schema_preview(form_schema: FormSchema) -> Dict[str, Any]:
        """
        Return a preview representation of the schema for rendering.
        """
        return FormRenderer.prepare_schema_preview(form_schema)

    # --- Submission processing --------------------------------------------

    async def process_submission(self, form_data: BaseModel) -> str:
        """
        Handle a validated form submission.

        - form_data is a Pydantic model instance (validated by your dynamic validation model).
        - This saves to DB using the repository which expects a Pydantic model and
          constructs the SQLAlchemy instance inside the repo.
        """
        data_dict = form_data.model_dump()
        logger.info(
            "form_submission_processing",
            data=data_dict,
            field_count=len(data_dict),
        )

        # Debug-only pretty print
        if settings.DEBUG:
            self._print_submission(data_dict)

        # Persist via repository; repo returns the inserted SQLAlchemy instance
        submission_response = await self.repo.insert_submission(form_data)
        submission_id = getattr(submission_response, "id", None)

        logger.info("form_submission_completed", submission_id=submission_id)
        return str(submission_id or "")

    @staticmethod
    def _print_submission(data: Dict[str, Any]) -> None:
        """Pretty-print submission to stdout — useful for local debugging."""
        print("\n" + "=" * 80)
        print("📝 FORM SUBMISSION RECEIVED")
        print("=" * 80)
        for field, value in data.items():
            formatted_field = f"{field}{'.' * max(0, (20 - len(field)))}"
            print(f"{formatted_field} {value}")
        print("=" * 80 + "\n")
