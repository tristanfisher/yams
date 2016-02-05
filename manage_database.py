import sys
from config import API, APP
from flask.ext.script import Manager, prompt_bool, prompt_choices, Command
from yams_api import api
from yams.app import db as app_db_sqla_instance
from yams_api.api import db as api_db_sqla_instance
manager_database = Manager(usage="Database Management")


valid_database_options = ['app', 'api']
def is_a_yams_db(db_name, db_options=valid_database_options):
    if db_name in db_options:
        return True
    return False

# todo: switch to "all" when using app-specific db


@manager_database.option("-db", "--database", dest="db", help="Specify the database to target.")
def create(db):
    """Create the databases necessary for YAMS to operate"""

    db = str(db).lower()
    if not is_a_yams_db(db):
        sys.exit("Unknown database.  YAMS has the following databases: %s.  Specify one with --database" % ", ".join(valid_database_options))

    if db == "app":
        app_db_sqla_instance.create_all()
    else:
        api_db_sqla_instance.create_all()


@manager_database.option("-db", "--database", dest="db", help="Specify the database to target.")
def drop(db):

    db = str(db).lower()
    if not is_a_yams_db(db):
        sys.exit("Unknown database.  YAMS has the following databases: %s.  Specify one with --database" % ", ".join(valid_database_options))

    prompt_str = "This is a destructive action that you *cannot* undo.  " \
                 "Are you sure you want to DROP DATABASES on: %s" % db
    if prompt_bool(prompt_str):
        if db == "app":
            app_db_sqla_instance.drop_all()
        else:
            api_db_sqla_instance.drop_all()


@manager_database.command
def show():
    print("APP DB => %s" %  APP.SQLALCHEMY_DATABASE_URI)
    print("API DB => %s" % API.SQLALCHEMY_DATABASE_URI)
