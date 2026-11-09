import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TransactionTag(str, enum.Enum):
    """
    Set by the rule engine (Phase 1) or the AI categorizer (Phase 2) —
    never written directly by the user. The user influences this indirectly
    by editing their budgets/rules.
    """

    GOOD = "good"
    BAD = "bad"
    NEUTRAL = "neutral"
    UNREVIEWED = "unreviewed"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    # Negative = money out (spend), positive = money in (income/saving).
    # This sign convention is what lets goal progress and balances be
    # derived purely by summing rows — see README section 2.3.
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    merchant: Mapped[str] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    tag: Mapped[TransactionTag] = mapped_column(
        Enum(TransactionTag, name="transaction_tag"), default=TransactionTag.UNREVIEWED
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="transactions")
    category: Mapped["Category | None"] = relationship()
    goal_contribution: Mapped["GoalContribution | None"] = relationship(
        back_populates="transaction", uselist=False
    )
    alerts: Mapped[list["Alert"]] = relationship(back_populates="transaction")
