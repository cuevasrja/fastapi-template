"""create users table

Revision ID: 0001
Revises:
Create Date: 2026-05-02

"""

from alembic import op

# revision identifiers, used by Alembic
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;

        CREATE TABLE users (
            id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
            email           VARCHAR(255) NOT NULL UNIQUE,
            hashed_password VARCHAR(255) NOT NULL,
            full_name       VARCHAR(100) NOT NULL,
            role            VARCHAR(50)  NOT NULL DEFAULT 'user',
            is_active       BOOLEAN      NOT NULL DEFAULT true,
            created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        );

        CREATE INDEX ix_users_email ON users (email);
    """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS ix_users_email;
        DROP TABLE IF EXISTS users;
    """)
