import sys
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Garante que o Python encontre os modulos do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa as configuracoes e o Base do SQLAlchemy
from app.config import settings
from app.infrastructure.database.connection import Base

# Importa todos os models para o Alembic detectar as tabelas automaticamente
import app.domain.models  # noqa: F401 - necessario para o Alembic

# Configuracao do Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Sobrescreve a URL do banco com o valor do arquivo .env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Metadados de todas as tabelas (necessario para autogenerate)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Roda migrations sem conexao ativa (modo offline)."""
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
    """Roda migrations com conexao ativa ao banco (modo normal)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
