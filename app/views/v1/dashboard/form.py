from typing import Annotated

from fastapi import Depends, Request, APIRouter
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from starlette import status

from app.common.logger import get_logger
from app.core.system import SystemManager, get_system_manager
from app.dependencies import get_form_service, get_validated_form_data
from app.jinja.form_renderer import FormRenderer
from app.jinja.templates import templates
from app.services.form_service import FormService

router = APIRouter(prefix="/form")

logger = get_logger()


@router.get(
    "/",
    name="show_form",
    response_class=HTMLResponse,
)
async def show_form(
        request: Request,
        system_manager: SystemManager = Depends(get_system_manager),
):
    """
    Loads the dynamic form schema from the service
    and renders the HTML form.
    """
    context = FormRenderer.create_form_context(
        form_schema=system_manager.get_form_schema(),
        form_title="Dynamic Form Submission",
        form_action=request.url_for("submit_form"),
    )

    return templates.TemplateResponse("form.html", {
        "request": request,
        "context": context,
    })


@router.post(
    "/submit",
    name="submit_form",
    response_class=HTMLResponse
)
async def submit_form(
        request: Request,
        form_service: Annotated[FormService, Depends(get_form_service)],
        system_manager: SystemManager = Depends(get_system_manager),
):
    try:
        validated_model = await get_validated_form_data(request, system_manager)
        submission_id = await form_service.process_submission(validated_model)

        success_context = FormRenderer.create_success_context(
            submission_id=submission_id,
            submitted_data=validated_model.model_dump(),
            form_title="Submission Successful!",
        )

        return templates.TemplateResponse(
            "success.html",
            {"request": request, **success_context}
        )

    except ValidationError as err:
        form = await request.form()
        form_schema = system_manager.get_form_schema()
        context = FormRenderer.create_form_context(
            form_schema=form_schema,
            values={
                k: (float(v) if "." in v else int(v)) if f.type == "number" and v else v
                for k, f in form_schema.fields.items()
                if (v := dict(form).get(k)) not in ("", None) or f.required
            },
            errors={
                err["loc"][0] if err["loc"] else "unknown": err["msg"]
                for err in err.errors()
            },
            form_title="Dynamic Form Submission",
        )

        return templates.TemplateResponse(
            "form.html",
            {"request": request, "context": context},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
