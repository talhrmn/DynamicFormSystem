from sqlalchemy.orm import registry, DeclarativeBase

# Global registry for all ORM models
mapper_registry = registry()


class Base(DeclarativeBase):
    """Base class shared by all SQLAlchemy models."""
    registry = mapper_registry
    metadata = mapper_registry.metadata
