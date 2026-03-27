"""Expand roles module with extended fields and audit trail

Revision ID: 9f5b0ca2d112
Revises: bd6017c922c1
Create Date: 2026-03-27 15:00:00.000000
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "9f5b0ca2d112"
down_revision = "bd6017c922c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("roles", sa.Column("icon_emoji", sa.String(length=32), nullable=True))
    op.add_column("roles", sa.Column("mentionable", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.alter_column("roles", "mentionable", server_default=None)

    op.create_table(
        "role_audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("guild_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=True),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("details", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["guild_id"], ["guilds.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_role_audit_logs_actor_id"), "role_audit_logs", ["actor_id"], unique=False)
    op.create_index(op.f("ix_role_audit_logs_guild_id"), "role_audit_logs", ["guild_id"], unique=False)
    op.create_index(op.f("ix_role_audit_logs_role_id"), "role_audit_logs", ["role_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_role_audit_logs_role_id"), table_name="role_audit_logs")
    op.drop_index(op.f("ix_role_audit_logs_guild_id"), table_name="role_audit_logs")
    op.drop_index(op.f("ix_role_audit_logs_actor_id"), table_name="role_audit_logs")
    op.drop_table("role_audit_logs")
    op.drop_column("roles", "mentionable")
    op.drop_column("roles", "icon_emoji")
