"""add ondelete cascade to fks

Revision ID: 392b29d79ec9
Revises: cb27406dc46e
Create Date: 2026-06-14 07:38:43.410680

Adds ON DELETE CASCADE to the child foreign keys so deleting a client (or account
or strategy) cascades through the hierarchy at the database level, matching the
ORM relationship cascades. Previously only accounts.client_id cascaded, so a raw
SQL `DELETE FROM clients` was blocked by strategies/trades/positions FKs.

Autogenerate does not detect ON DELETE changes, so this migration is hand-written.
It is a no-op on SQLite (tests build the schema from the models via create_all).
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "392b29d79ec9"
down_revision = "cb27406dc46e"
branch_labels = None
depends_on = None


# (constraint_name, table, ref_table, local_col, remote_col)
_FKS = [
    ("strategies_client_id_fkey", "strategies", "clients", "client_id", "id"),
    ("strategies_account_id_fkey", "strategies", "accounts", "account_id", "id"),
    ("trades_strategy_id_fkey", "trades", "strategies", "strategy_id", "id"),
    ("positions_strategy_id_fkey", "positions", "strategies", "strategy_id", "id"),
    (
        "sheet_sync_configs_client_id_fkey",
        "sheet_sync_configs",
        "clients",
        "client_id",
        "id",
    ),
    (
        "sheet_sync_configs_strategy_id_fkey",
        "sheet_sync_configs",
        "strategies",
        "strategy_id",
        "id",
    ),
]


def _recreate(ondelete):
    for name, table, ref, local, remote in _FKS:
        op.drop_constraint(name, table, type_="foreignkey")
        op.create_foreign_key(name, table, ref, [local], [remote], ondelete=ondelete)


def upgrade() -> None:
    # FK ALTER via drop/recreate is Postgres-specific; SQLite gets cascade from
    # the models through create_all, so skip there.
    if op.get_bind().dialect.name != "postgresql":
        return
    _recreate("CASCADE")


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    _recreate(None)
