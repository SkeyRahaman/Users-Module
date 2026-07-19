from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from app.config import Config as AppConfig


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
import os
#Application Configuration
APPLICATION_NAME = os.getenv("APPLICATION_NAME","Users_Module")
# Database Configuration
DATABASE_DRIVER_SYNC = os.getenv("DATABASE_DRIVER_SYNC","sqlite")
if DATABASE_DRIVER_SYNC.startswith("sqlite"):
    DATABASE_URL_ALEMBIC = os.getenv("DATABASE_URL_ALEMBIC",f"sqlite:///./{APPLICATION_NAME}.db")
else:
    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME","user")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD","password")
    DATABASE_HOST = os.getenv("DATABASE_HOST","localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT","5432")
    DATABASE_URL_ALEMBIC = os.getenv("DATABASE_URL_ALEMBIC",f"{DATABASE_DRIVER_SYNC}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{APPLICATION_NAME}")

config.set_main_option("sqlalchemy.url", DATABASE_URL_ALEMBIC)


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from app.database.models import Base  # Your declarative base
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
