from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# Đảm bảo load models
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from models import Base  # noqa: E402

# Alembic Config object
config = context.config

# Load biến môi trường từ .env
load_dotenv()

# Lấy DATABASE_URL từ env
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("❌ DATABASE_URL is not set in your .env file")

# Gán vào alembic config
config.set_main_option("sqlalchemy.url", database_url)

# Logging config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata cho autogenerate
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
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
