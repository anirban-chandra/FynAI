# Import every model here so Alembic's autogenerate can discover them via
# Base.metadata. If you add a new model file, add its import below.

from app.models.user import User  # noqa: F401
from app.models.goal import Goal, GoalContribution  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.transaction import Transaction, TransactionTag  # noqa: F401
from app.models.budget import Budget  # noqa: F401
from app.models.alert import Alert, AlertType  # noqa: F401
