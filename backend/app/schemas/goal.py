import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class GoalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    target_amount: Decimal = Field(gt=0, decimal_places=2)
    target_date: date


class GoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    target_amount: Decimal
    target_date: date
    created_at: datetime


class GoalProgress(BaseModel):
    """
    Computed, not stored — built by services/goal_progress.py from the sum
    of linked transactions. Returned alongside GoalRead on the dashboard
    endpoint (Week 4/7).
    """

    goal_id: uuid.UUID
    saved_so_far: Decimal
    percent_complete: float
    days_remaining: int
    required_monthly_savings: Decimal
