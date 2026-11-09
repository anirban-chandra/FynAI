import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import TransactionTag


class TransactionCreate(BaseModel):
    # Negative = spend, positive = income/saving (see README section 2.3).
    amount: Decimal = Field(decimal_places=2)
    merchant: str | None = Field(default=None, max_length=255)
    note: str | None = Field(default=None, max_length=500)
    occurred_at: datetime
    category_id: uuid.UUID | None = None
    goal_id: uuid.UUID | None = None  # optional: link this transaction to a goal


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    amount: Decimal
    merchant: str | None
    note: str | None
    occurred_at: datetime
    category_id: uuid.UUID | None
    tag: TransactionTag
    created_at: datetime
