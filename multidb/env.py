from __future__ import with_statement
import os
import sys
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# We need to go back a dir to get the config.
_this_dir = os.path.dirname((os.path.abspath(__file__)))
_parent_dir = os.path.join(_this_dir, '../')
for _p in (_this_dir, _parent_dir):
    if _p not in sys.path:
        sys.path.append(_p)

from config import API, APP

# Bind some vars for our migrations to use for environmental setup
API_URL_WITH_SLASH = API.LISTEN_URL + "/"

#
# n.b. this is only currently doing API migrations
#


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
def merged_ini_py_conf():
    """Update some settings that would be fetched from the ini with those from our
     application config.
    this could maybe be cleaner with some clever .setdefault('key', default_value)
    :return: merged settings dict
    """

    conf = config.get_section(config.config_ini_section)

    if hasattr(API, 'SQLALCHEMY_DATABASE_URI'):
        conf['sqlalchemy.url'] = API.SQLALCHEMY_DATABASE_URI

    return conf

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=merged_ini_py_conf().get('sqlalchemy.url'),
        target_metadata=target_metadata,
        literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = engine_from_config(
        merged_ini_py_conf(),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
