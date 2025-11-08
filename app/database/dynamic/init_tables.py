from app.core.config import get_settings
from app.core.system import get_system_manager
from app.database.database import engine
from app.database.dynamic.model_factory import create_dynamic_model
from app.database.dynamic.table_manager import create_table_if_not_exists

settings = get_settings()
system_manager = get_system_manager()

async def init_dynamic_tables():
    """
    Load schema, generate dynamic model, and ensure table exists.
    """
    form_schema = system_manager.get_form_schema()
    Model = create_dynamic_model(form_schema, settings.DATABASE_TABLE_NAME)

    await create_table_if_not_exists(Model, engine)
    return Model
