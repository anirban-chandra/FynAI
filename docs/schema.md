# Schema Notes

Expanded detail on the data model summarized in the root README. Update this
file whenever a model changes — the README diagram should stay high-level,
this file carries the reasoning.

## Why `amount` is signed, not split into separate `income`/`expense` tables

A single signed `amount` column on `transactions` (negative = spend, positive
= income/saving) means:
- Goal progress = `SUM(amount)` across linked transactions. No separate
  "current saved" field to keep in sync.
- A category's monthly spend = `SUM(amount) WHERE amount < 0 AND category_id = X
  AND occurred_at BETWEEN ...`. One query, no join complexity.
- Refunds/corrections are just another transaction row, not an update to a
  historical record — preserves the audit trail, which matters a lot once
  real bank data (Phase 3) starts flowing in and users expect to see exactly
  what happened and when.

## Why `tag` lives on the transaction, not computed on every read

`transactions.tag` is a stored, indexed column (not computed at query time)
because:
- The dashboard needs to filter/aggregate by tag frequently (e.g. "show my
  good vs bad spend this month") — recomputing on every read would mean
  re-running the rule engine against every budget on every dashboard load.
- It gives us a natural place to show the *history* of how a transaction was
  tagged, which becomes important in Phase 2 when the AI categorizer
  replaces the rule engine — we can compare old vs new tagging behavior.

The tradeoff: if a user edits a budget rule retroactively, old transactions
don't automatically re-tag. A background re-tagging job is a reasonable
Phase 2 addition once this limitation is actually felt by users — not before.

## Why `categories` allows `user_id IS NULL`

System-default categories (Rent, Dining, Transport, etc.) are seeded once
with `user_id = NULL` and `is_system_default = TRUE`, and every user sees
them automatically. A user can still add their own categories (`user_id` set
to their own id). This avoids duplicating the same 15-20 rows per user while
still allowing personalization.

## Open questions to resolve before Week 6 (rule engine)

- Should a transaction be allowed to belong to *multiple* categories (e.g.
  split a single bill), or exactly one? Current schema assumes exactly one
  (`category_id` is a single FK). Revisit only if real usage demands it.
- Should `goal_contributions` allow a transaction to fund multiple goals
  partially? Current schema assumes one transaction → at most one goal.
  Flagged as a deliberate Phase 1 simplification in the README.
