from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional, Type, Dict, Any

from pydantic import BaseModel

from app.common.exceptions.exceptions import InvalidSchemaException, SchemaNotLoadedException, SchemaMissingException, \
    TableModelException
from app.common.logger import get_logger
from app.common.schemas import FormSchema
from app.schemas.dynamic.model_factory import generate_dynamic_pydantic_model

logger = get_logger()


class SystemManager:
    """
    System instance to manage generated data.
    Initialized once and cached.
    """

    def __init__(self):
        self.form_schema: Optional[FormSchema] = None
        self.validation_model: Optional[Type[BaseModel]] = None
        self.table_model: Optional[type] = None
        self._schema_dict: Optional[Dict[str, Any]] = None
        self.schema_loaded: bool = False

    def load_schema_from_file(self, file_path: str) -> None:
        """
        Load schema from a JSON file.
        """
        path = Path(file_path)

        if not path.exists():
            logger.warning(
                "schema_file_not_found",
                file=str(path),
                action="loading_default_schema",
            )
            raise SchemaMissingException(f"Schema file not found")

        try:
            with path.open("r") as f:
                schema_dict = json.load(f)

            self._load_schema(schema_dict)
            logger.info("schema_loaded_from_file", file=str(path))

        except json.JSONDecodeError as e:
            logger.error("schema_invalid_json", file=str(path), error=str(e))
            raise InvalidSchemaException(f"Invalid JSON in schema file: {e}")

        except Exception as e:
            logger.error("schema_load_error", file=str(path), error=str(e))
            raise InvalidSchemaException(f"Unexpected error loading schema: {e}")

    def _load_schema(self, schema_dict: Dict[str, Any]) -> None:
        """
        Parse and store the form schema + generated validation model.
        """
        try:
            self._schema_dict = schema_dict
            self.form_schema = FormSchema.from_dict(schema_dict)

            self.validation_model = generate_dynamic_pydantic_model(
                schema=self.form_schema,
                model_name="DynamicFormModel"
            )

            self.schema_loaded = True

            logger.info(
                "schema_loaded",
                fields=self.form_schema.get_field_names(),
                required=self.form_schema.get_required_fields(),
                count=len(self.form_schema.fields),
            )

        except Exception as e:
            logger.error("schema_load_failed", error=str(e))
            raise InvalidSchemaException(f"Failed to load schema: {e}")

    def get_validation_model(self) -> Type[BaseModel]:
        """Return the generated Pydantic validation model."""
        if not self.schema_loaded or not self.validation_model:
            raise SchemaNotLoadedException()
        return self.validation_model

    def get_form_schema(self) -> FormSchema:
        """Return the loaded FormSchema."""
        if not self.schema_loaded or not self.form_schema:
            raise SchemaNotLoadedException()
        return self.form_schema

    def get_schema_dict(self) -> Dict[str, Any]:
        """Return the original schema dictionary."""
        if not self.schema_loaded or not self._schema_dict:
            raise SchemaNotLoadedException()
        return self._schema_dict

    def set_table_model(self, table_model: type) -> None:
        """Return the generated Pydantic validation model."""
        self.table_model = table_model

    def get_table_model(self) -> type:
        """Return the original schema dictionary."""
        if not self.table_model:
            raise TableModelException()
        return self.table_model


@lru_cache()
def get_system_manager() -> SystemManager:
    """Return a cached SystemManager instance."""
    return SystemManager()
