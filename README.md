# FynAI — Personal Finance Goals & AI-Guided Spending

> **Status:** Week 1 scaffold — schema + repo structure only. No business logic yet.

FynAI helps people set financial goals (save ₹X in Y months), track transactions against
those goals, and get nudged away from spending that works against them. Long-term, it layers
an AI "advisor" on top of the user's own transaction history, and pulls real bank transactions
in via India's Account Aggregator (AA) framework instead of manual entry.

This repo is being built in phases. **This README documents the end-state architecture**, not
just what exists today — sections are marked with phase numbers so you know what's scaffolded
vs. what's planned.

---

## 1. Project Workflow (how a user moves through the app)

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│  1. Sign up  │ ──▶ │ 2. Set a     │ ──▶ │ 3. Log /sync  │ ──▶ │ 4. See       │
│  / Log in    │     │   goal       │     │   transactions│     │   dashboard  │
└─────────────┘     └──────────────┘     └───────────────┘     └──────────────┘
                                                  │                     │
                                                  ▼                     ▼
                                          ┌───────────────┐    ┌──────────────┐
                                          │ 5. Rule engine │    │ 6. Alerts /  │
                                          │  tags good/bad │──▶ │   nudges     │
                                          └───────────────┘    └──────────────┘
                                                  │
                                                  ▼ (Phase 2+)
                                          ┌───────────────┐
                                          │ 7. AI advisor  │
                                          │  explains &    │
                                          │  recommends    │
                                          └───────────────┘
```

**Phase 1 (this repo, weeks 1–12):** steps 1–6, with transactions entered **manually** and
categorization driven by **user-defined rules** (no AI yet). This is deliberate — rule-based
categorization is cheap to build and lets us validate the goal-tracking idea before investing
in AI or bank integrations.

**Phase 2 (later):** step 7 — LLM-based categorization and a chat-style advisor that reasons
over the user's own data (RAG-style).

**Phase 3 (later):** step 3 becomes automatic via the Account Aggregator framework (RBI-regulated
consent-based bank data sharing), replacing manual entry.

---

## 2. System Architecture

### 2.1 High-level component diagram (target state, Phase 1–3)

```
┌────────────────────────────────────────────────────────────────────┐
│                           Frontend (Next.js)                       │
│   Dashboard · Goals UI · Transactions UI · Alerts UI · Auth pages  │
└───────────────────────────────┬──────────────────────────────────┘
                                 │ REST (JSON over HTTPS)
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│                         Backend (FastAPI)                          │
│  ┌───────────┐ ┌───────────┐ ┌────────────┐ ┌───────────────────┐ │
│  │   Auth    │ │   Goals   │ │Transactions│ │   Rule Engine /    │ │
│  │  (JWT)    │ │  Service  │ │  Service   │ │  Categorization    │ │
│  └───────────┘ └───────────┘ └────────────┘ └───────────────────┘ │
│  ┌───────────┐ ┌───────────────────────┐ ┌─────────────────────┐  │
│  │  Alerts   │ │   AI Advisor (Phase2) │ │ AA Connector(Phase3)│  │
│  │  Service  │ │   LLM + RAG over txns │ │ FIU client (Setu/   │  │
│  └───────────┘ └───────────────────────┘ │ Finvu sandbox)       │  │
│                                           └─────────────────────┘  │
└───────────────────────────────┬──────────────────────────────────┘
                                 │ SQL (SQLAlchemy ORM)
                                 ▼
                      ┌─────────────────────┐
                      │   PostgreSQL         │
                      │  users, goals,       │
                      │  transactions,       │
                      │  categories, budgets,│
                      │  alerts              │
                      └─────────────────────┘
```

### 2.2 Why these choices

| Decision | Reasoning |
|---|---|
| **PostgreSQL, not NoSQL** | Financial data needs relational integrity (foreign keys between users/goals/transactions) and ACID transactions. A user's balance must never be computed from an inconsistent read. |
| **Transactions are an append-only ledger** | We never store a mutable "current balance" field. Balances and goal progress are always *derived* by summing transactions. This avoids an entire class of sync bugs. |
| **FastAPI over Django** | Async-native, automatic OpenAPI docs (useful once the frontend and backend are built by the same person — fewer integration bugs), Pydantic validation forces you to define data shapes explicitly, which matters a lot for financial fields (no silent type coercion). |
| **Next.js over plain React** | File-based routing, built-in API proxying, easy deploy to Vercel — less boilerplate for a solo/part-time builder. |
| **Rule engine before AI (Phase 1 vs Phase 2)** | Validates the core premise (do people want goal-linked categorization?) before spending weeks on LLM integration costs and prompt design. |
| **Account Aggregator deferred to Phase 3** | AA integration requires sandbox approval, request signing, and eventually production licensing review — treating this as week-1 work would block everything else. Manual entry is a fully functional substitute for Phase 1–2. |

### 2.3 Data model (Week 1 deliverable)

```
users
 ├── id (PK)
 ├── email (unique)
 ├── hashed_password
 ├── created_at
 │
 ├──< goals (user_id FK)
 │      ├── id (PK)
 │      ├── title              e.g. "Emergency fund"
 │      ├── target_amount
 │      ├── target_date
 │      ├── created_at
 │      │
 │      └──< goal_contributions (goal_id FK, transaction_id FK)
 │             (join table: which transactions count toward which goal)
 │
 ├──< categories (user_id FK, nullable = system default category)
 │      ├── id (PK)
 │      ├── name                e.g. "Dining out"
 │      └── is_system_default
 │
 ├──< budgets (user_id FK, category_id FK)
 │      ├── id (PK)
 │      ├── monthly_limit
 │      └── period_start
 │
 ├──< transactions (user_id FK, category_id FK nullable)
 │      ├── id (PK)
 │      ├── amount              (negative = spend, positive = income/saving)
 │      ├── merchant
 │      ├── note
 │      ├── occurred_at
 │      ├── tag                 enum: good | bad | neutral | unreviewed
 │      └── created_at
 │
 └──< alerts (user_id FK, transaction_id FK nullable)
        ├── id (PK)
        ├── type                enum: budget_exceeded | goal_at_risk | ...
        ├── message
        ├── is_read
        └── created_at
```

**Key design rule:** `transactions.tag` is set by the rule engine (Phase 1) or the LLM
(Phase 2), never typed directly by the user — the user instead edits the *rules* (budgets)
that drive the tag. This keeps the categorization logic centralized and swappable.

---

## 3. Repo Structure

```
FynAI/
├── README.md                    ← you are here
├── docker-compose.yml           ← spins up postgres + backend + frontend locally
├── .github/workflows/ci.yml     ← lint + test on every push
│
├── backend/                     ← FastAPI service
│   ├── app/
│   │   ├── main.py              ← FastAPI app entrypoint
│   │   ├── core/
│   │   │   ├── config.py        ← env var loading (Pydantic Settings)
│   │   │   └── security.py      ← password hashing, JWT creation/validation
│   │   ├── db/
│   │   │   ├── base.py          ← SQLAlchemy declarative base
│   │   │   └── session.py       ← DB session/connection management
│   │   ├── models/               ← SQLAlchemy ORM models (one file per table)
│   │   │   ├── user.py
│   │   │   ├── goal.py
│   │   │   ├── transaction.py
│   │   │   ├── category.py
│   │   │   ├── budget.py
│   │   │   └── alert.py
│   │   ├── schemas/              ← Pydantic request/response models
│   │   │   ├── user.py
│   │   │   ├── goal.py
│   │   │   └── transaction.py
│   │   ├── api/v1/endpoints/     ← route handlers, one file per resource
│   │   │   ├── auth.py
│   │   │   ├── goals.py
│   │   │   └── transactions.py
│   │   └── services/             ← business logic (kept out of route handlers)
│   │       ├── rule_engine.py    ← Week 6: good/bad tagging logic
│   │       └── goal_progress.py  ← progress % and required savings rate calc
│   ├── alembic/                  ← DB migrations (versioned schema changes)
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                     ← Next.js app
│   ├── src/
│   │   ├── app/                  ← pages (App Router)
│   │   ├── components/           ← shared UI components
│   │   ├── lib/                  ← API client, auth helpers
│   │   └── types/                ← TypeScript types mirroring backend schemas
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
└── docs/
    └── schema.md                 ← detailed schema notes (expand as you add tables)
```

---

## 4. Local Development

```bash
# 1. Clone and set up environment variables
cp backend/.env.example backend/.env

# 2. Start everything (postgres + backend + frontend)
docker-compose up --build

# Backend:  http://localhost:8000  (docs at /docs — FastAPI auto-generates these)
# Frontend: http://localhost:3000
```

---

## 5. Roadmap Reference

This repo follows the phased plan below. Each phase is a separate milestone, not a separate
repo — branches/tags will mark phase boundaries.

- **Phase 1 (Weeks 1–12):** Core app — auth, goals, manual transactions, rule-based
  categorization, budgets, alerts, dashboard. *(this scaffold)*
- **Phase 2 (Months 3–5):** AI categorization + conversational advisor (LLM + RAG over the
  user's own transaction history).
- **Phase 3 (Months 5–8):** Account Aggregator integration (automatic bank transaction sync,
  RBI-regulated consent framework) — replaces manual entry.
- **Phase 4 (Months 8–10):** Billing, compliance hardening (DPDP Act), security audit, beta
  launch.

See project notes for the detailed week-by-week breakdown of each phase.
