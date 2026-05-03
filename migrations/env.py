from logging.config import fileConfig

from alembic import context
from sqlalchemy import MetaData, create_engine

from app.core.config import settings

config = context.config

# Convert standard postgresql:// URL to sqlalchemy+psycopg dialect for Alembic
migration_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
config.set_main_option("sqlalchemy.url", migration_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Migrations are written as raw SQL — no ORM metadata to autogenerate from
target_metadata = MetaData()


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(migration_url)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
