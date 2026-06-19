"""case-insensitive unique strategy names

Revision ID: 95798c4a2a9a
Revises: fe521b07fb54
Create Date: 2026-06-14 10:05:00.000000

Adds a unique functional index on ``lower(strategies.name)`` so that strategy
definitions are unique case-insensitively ("Growth" and "growth" collide). The
auto-route CSV import and the POST /strategies endpoint both resolve strategy
names case-insensitively, and this enforces it at the database level.

Portable expression index (works on PostgreSQL and SQLite). Assumes no existing
case-duplicate strategy names — true after the split migration (which deduped by
exact name) unless variants were created manually; collapse any such rows before
upgrading.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "95798c4a2a9a"
down_revision = "fe521b07fb54"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_strategy_name_lower",
        "strategies",
        [sa.text("lower(name)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_strategy_name_lower", table_name="strategies")
