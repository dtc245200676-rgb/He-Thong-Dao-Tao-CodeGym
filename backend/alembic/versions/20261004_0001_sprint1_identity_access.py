"""Sprint 1 identity, session and RBAC schema.

Revision ID: 20261004_0001
Revises:
Create Date: 2026-10-04
"""

from alembic import op
import sqlalchemy as sa

revision = "20261004_0001"
down_revision = None
branch_labels = None
depends_on = None


def _table_names(bind):
    return set(sa.inspect(bind).get_table_names())


def _column_names(bind, table_name: str):
    return {col["name"] for col in sa.inspect(bind).get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    tables = _table_names(bind)

    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("full_name", sa.String(150), nullable=False, server_default=""),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("phone", sa.String(30), nullable=True),
            sa.Column("password_hash", sa.String(255), nullable=False),
            sa.Column("role", sa.String(50), nullable=False, server_default="student"),
            sa.Column("status", sa.String(20), nullable=False, server_default="active"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("needs_handover", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("locked_until", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("email", name="uq_users_email"),
        )
        op.create_index("ix_users_email", "users", ["email"], unique=True)
        op.create_index("ix_users_phone", "users", ["phone"], unique=False)
        op.create_index("ix_users_status", "users", ["status"], unique=False)
    else:
        cols = _column_names(bind, "users")
        additions = [
            ("full_name", sa.Column("full_name", sa.String(150), nullable=False, server_default="")),
            ("phone", sa.Column("phone", sa.String(30), nullable=True)),
            ("status", sa.Column("status", sa.String(20), nullable=False, server_default="active")),
            ("must_change_password", sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default=sa.text("0"))),
            ("needs_handover", sa.Column("needs_handover", sa.Boolean(), nullable=False, server_default=sa.text("0"))),
            ("updated_at", sa.Column("updated_at", sa.DateTime(), nullable=True)),
        ]
        for name, column in additions:
            if name not in cols:
                op.add_column("users", column)
        # The prototype already had created_at/role/is_active/login lock fields.
        op.execute("UPDATE users SET status = CASE WHEN is_active = 1 THEN 'active' ELSE 'locked' END WHERE status IS NULL OR status = ''")

    tables = _table_names(bind)
    if "roles" not in tables:
        op.create_table(
            "roles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("slug", sa.String(50), nullable=False),
            sa.Column("name", sa.String(100), nullable=False),
            sa.Column("description", sa.String(255), nullable=True),
            sa.UniqueConstraint("slug", name="uq_roles_slug"),
        )
        op.create_index("ix_roles_slug", "roles", ["slug"], unique=True)

    if "permissions" not in tables:
        op.create_table(
            "permissions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code", sa.String(100), nullable=False),
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("description", sa.String(255), nullable=True),
            sa.UniqueConstraint("code", name="uq_permissions_code"),
        )
        op.create_index("ix_permissions_code", "permissions", ["code"], unique=True)

    tables = _table_names(bind)
    if "user_roles" not in tables:
        op.create_table(
            "user_roles",
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        )

    if "role_permissions" not in tables:
        op.create_table(
            "role_permissions",
            sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("permission_id", sa.Integer(), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
        )

    if "auth_sessions" not in tables:
        op.create_table(
            "auth_sessions",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("last_activity_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("revoked_at", sa.DateTime(), nullable=True),
            sa.Column("user_agent", sa.String(255), nullable=True),
        )
        op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
        op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])
        op.create_index("ix_auth_sessions_revoked_at", "auth_sessions", ["revoked_at"])

    if "password_reset_tokens" not in tables:
        op.create_table(
            "password_reset_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("used_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
        op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"], unique=True)
        op.create_index("ix_password_reset_tokens_expires_at", "password_reset_tokens", ["expires_at"])

    if "activation_tokens" not in tables:
        op.create_table(
            "activation_tokens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("used_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_activation_tokens_user_id", "activation_tokens", ["user_id"])
        op.create_index("ix_activation_tokens_token_hash", "activation_tokens", ["token_hash"], unique=True)
        op.create_index("ix_activation_tokens_expires_at", "activation_tokens", ["expires_at"])

    if "account_lock_audits" not in tables:
        op.create_table(
            "account_lock_audits",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("action", sa.String(20), nullable=False),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_account_lock_audits_user_id", "account_lock_audits", ["user_id"])


def downgrade() -> None:
    bind = op.get_bind()
    tables = _table_names(bind)
    for table in [
        "account_lock_audits",
        "activation_tokens",
        "password_reset_tokens",
        "auth_sessions",
        "role_permissions",
        "user_roles",
        "permissions",
        "roles",
    ]:
        if table in tables:
            op.drop_table(table)
    # Keep users and its data on downgrade because this project may have started
    # with the prototype users table before Alembic was introduced.
