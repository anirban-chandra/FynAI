from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Shared declarative base for all ORM models. Every model in app/models/
    inherits from this so Alembic can discover them for migrations.
    """

    pass
