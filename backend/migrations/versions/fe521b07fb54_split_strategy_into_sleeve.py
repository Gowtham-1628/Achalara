"""split strategy into global definition + sleeve

Revision ID: fe521b07fb54
Revises: 392b29d79ec9
Create Date: 2026-06-14 09:10:00.000000

Splits the old per-account ``strategies`` table into two concepts:

- ``strategies`` becomes a firm-wide (global) definition: just name + description.
- a new ``sleeves`` table = a strategy as run within one account
  (account_id + strategy_id). ``trades``, ``positions`` and ``sheet_sync_configs``
  reparent from ``strategy_id`` onto ``sleeve_id``.

Key trick that avoids rewriting child FK values: each old strategy row's id is
preserved as its Sleeve id, so existing ``strategy_id`` values on the child tables
already equal the right ``sleeve.id`` — we only rename the column and repoint the FK.
Old per-account strategies are deduped by name into global definitions.

Postgres-only body (guarded by dialect). SQLite/tests build the schema from the
models via ``create_all`` so this is a no-op there. Safe on an empty database: the
data-backfill INSERT...SELECTs simply move zero rows while the DDL still runs.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fe521b07fb54"
down_revision = "392b29d79ec9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    # 1. sleeves table — account FK + unique now; strategy FK added at the end
    #    (the global strategy rows it references don't exist yet).
    op.create_table(
        "sleeves",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("account_id", sa.String(length=36), nullable=False),
        sa.Column("strategy_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "account_id", "strategy_id", name="uq_sleeve_account_strategy"
        ),
    )

    # 2. Map each distinct strategy name to a fresh global strategy id.
    op.execute(
        """
        CREATE TEMP TABLE strat_map AS
        SELECT DISTINCT ON (name)
               name,
               gen_random_uuid()::text AS new_id,
               description
        FROM strategies
        ORDER BY name, id
        """
    )

    # 3. One sleeve per old strategy row, preserving the old id as the sleeve id.
    op.execute(
        """
        INSERT INTO sleeves (id, account_id, strategy_id, created_at, updated_at)
        SELECT s.id, s.account_id, m.new_id, s.created_at, s.updated_at
        FROM strategies s
        JOIN strat_map m USING (name)
        """
    )

    # 4. Reparent children: values already equal the right sleeve.id.
    # trades
    op.drop_constraint("trades_strategy_id_fkey", "trades", type_="foreignkey")
    op.alter_column("trades", "strategy_id", new_column_name="sleeve_id")
    op.create_foreign_key(
        "trades_sleeve_id_fkey",
        "trades",
        "sleeves",
        ["sleeve_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # positions
    op.drop_constraint("positions_strategy_id_fkey", "positions", type_="foreignkey")
    op.alter_column("positions", "strategy_id", new_column_name="sleeve_id")
    op.create_foreign_key(
        "positions_sleeve_id_fkey",
        "positions",
        "sleeves",
        ["sleeve_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_position_sleeve_symbol", "positions", ["sleeve_id", "symbol"]
    )
    # sheet_sync_configs (also drop the now-derivable client_id)
    op.drop_constraint(
        "sheet_sync_configs_strategy_id_fkey", "sheet_sync_configs", type_="foreignkey"
    )
    op.drop_constraint(
        "sheet_sync_configs_client_id_fkey", "sheet_sync_configs", type_="foreignkey"
    )
    op.alter_column("sheet_sync_configs", "strategy_id", new_column_name="sleeve_id")
    op.create_foreign_key(
        "sheet_sync_configs_sleeve_id_fkey",
        "sheet_sync_configs",
        "sleeves",
        ["sleeve_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_column("sheet_sync_configs", "client_id")

    # 5. Collapse strategies into global definitions.
    op.drop_constraint("strategies_account_id_fkey", "strategies", type_="foreignkey")
    op.drop_constraint("strategies_client_id_fkey", "strategies", type_="foreignkey")
    op.execute("DELETE FROM strategies")  # remove old per-account rows
    op.drop_column("strategies", "account_id")
    op.drop_column("strategies", "client_id")
    op.execute(
        """
        INSERT INTO strategies (id, name, description, created_at, updated_at)
        SELECT new_id, name, description, now(), now()
        FROM strat_map
        """
    )

    # 6. Now that global strategy rows exist, add the deferred sleeve FK.
    op.create_foreign_key(
        "sleeves_strategy_id_fkey",
        "sleeves",
        "strategies",
        ["strategy_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.execute("DROP TABLE strat_map")


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    # Reconstruct the old per-account strategy rows from sleeves (ids were preserved).
    op.drop_constraint("sleeves_strategy_id_fkey", "sleeves", type_="foreignkey")

    op.add_column(
        "strategies", sa.Column("account_id", sa.String(length=36), nullable=True)
    )
    op.add_column(
        "strategies", sa.Column("client_id", sa.String(length=36), nullable=True)
    )

    # Re-create one strategy row per sleeve (sleeve.id == old strategy id), then drop
    # the global definition rows.
    op.execute(
        """
        INSERT INTO strategies
            (id, account_id, client_id, name, description, created_at, updated_at)
        SELECT sl.id, sl.account_id, a.client_id, st.name, st.description,
               sl.created_at, sl.updated_at
        FROM sleeves sl
        JOIN accounts a ON a.id = sl.account_id
        JOIN strategies st ON st.id = sl.strategy_id
        """
    )
    op.execute(
        """
        DELETE FROM strategies
        WHERE id NOT IN (SELECT id FROM sleeves)
        """
    )

    op.alter_column("strategies", "account_id", nullable=False)
    op.alter_column("strategies", "client_id", nullable=False)
    op.create_foreign_key(
        "strategies_account_id_fkey",
        "strategies",
        "accounts",
        ["account_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "strategies_client_id_fkey",
        "strategies",
        "clients",
        ["client_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Reparent children back onto strategy_id (values already == old strategy ids).
    op.drop_constraint(
        "sheet_sync_configs_sleeve_id_fkey", "sheet_sync_configs", type_="foreignkey"
    )
    op.add_column(
        "sheet_sync_configs",
        sa.Column("client_id", sa.String(length=36), nullable=True),
    )
    op.execute(
        """
        UPDATE sheet_sync_configs c
        SET client_id = a.client_id
        FROM sleeves sl
        JOIN accounts a ON a.id = sl.account_id
        WHERE c.sleeve_id = sl.id
        """
    )
    op.alter_column("sheet_sync_configs", "client_id", nullable=False)
    op.alter_column("sheet_sync_configs", "sleeve_id", new_column_name="strategy_id")
    op.create_foreign_key(
        "sheet_sync_configs_strategy_id_fkey",
        "sheet_sync_configs",
        "strategies",
        ["strategy_id"],
        ["id"],
    )
    op.create_foreign_key(
        "sheet_sync_configs_client_id_fkey",
        "sheet_sync_configs",
        "clients",
        ["client_id"],
        ["id"],
    )

    op.drop_constraint("uq_position_sleeve_symbol", "positions", type_="unique")
    op.drop_constraint("positions_sleeve_id_fkey", "positions", type_="foreignkey")
    op.alter_column("positions", "sleeve_id", new_column_name="strategy_id")
    op.create_foreign_key(
        "positions_strategy_id_fkey", "positions", "strategies", ["strategy_id"], ["id"]
    )

    op.drop_constraint("trades_sleeve_id_fkey", "trades", type_="foreignkey")
    op.alter_column("trades", "sleeve_id", new_column_name="strategy_id")
    op.create_foreign_key(
        "trades_strategy_id_fkey", "trades", "strategies", ["strategy_id"], ["id"]
    )

    op.drop_table("sleeves")
