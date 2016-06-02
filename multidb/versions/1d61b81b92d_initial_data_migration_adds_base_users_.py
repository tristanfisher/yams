"""Initial data migration.  Adds base users and example dashboard.

Revision ID: 1d61b81b92d
Revises: 
Create Date: 2016-02-04 22:13:06.235243


This file is part of YAMS.
YAMS is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
"""

import os
import sys
from importlib import import_module
from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as SessionBase, relationship
# Get the env.py-containing dir for the config -- otherwise, we'd have to make bad assumptions about the install env.

_this_dir = os.path.dirname((os.path.abspath(__file__)))
_parent_dir = os.path.join(_this_dir, '../')
_pparent_dir = os.path.join(_this_dir, '../../')
for _p in (_this_dir, _parent_dir, _pparent_dir):
    if _p not in sys.path:
        sys.path.append(_p)

from config import API

# Load the version of core specified by the user to pin
try:
    _api_user_module = import_module(name="yams_api.core.%s.user" % API.API_VERSION_CORE)
    _api_user_module_models = _api_user_module.models
    _api_utils = import_module(name="yams_api.core.%s.utils" % API.API_VERSION_CORE)
except ImportError as e:
    exit("Failed to load core version : %s <%s>" % (API.API_VERSION_CORE, e))



# revision identifiers, used by Alembic.
revision = '1d61b81b92d'
down_revision = None
branch_labels = None
depends_on = None


test_dashboard = [
    {
        "id": 1,
        "label": "amazon",
        "boxes": [
            {
                "id": 1,
                "label": "api status",
                "width": "25%",
                "height": "100%",
                "data": {
                    "update_method": {
                        "interval_seconds": 30, "type": "polling"
                    },
                    "endpoint": API.SQLALCHEMY_DATABASE_URI + "plugins/aws/status",
                    # vs series, etc
                    "data_type": "spot",
                    "field": {"response": {"response": "status"}},
                    "field_type": "glob_string",
                    "display_type": "list",
                    "detail_text_field": {'response': 'response'}
                },
                "enabled": 0
            }
        ]
    },
    {
        "id": 2,
        "label": "third parties",
        "boxes": [
            {
                "id": 1,
                "label": "github status",
                "width": "25%",
                "height": "100%",
                "data": {
                    "update_method": {
                        "interval_seconds": 30, "type": "polling"
                    },
                    "endpoint": API.SQLALCHEMY_DATABASE_URI  + "plugins/github/status",
                    "data_type": "spot",
                    "logic": "boolean",
                    "field": {"response":"status"},
                    "field_type": "string",
                    "display_type": "list",
                    "detail_text_field": {'response': 'response'},
                },
                "enabled": 1
            },
            {
                "id": 2,
                "label": "dropbox status",
                "width": "25%",
                "height": "100%",
                "data": {
                    "update_method": {
                        "interval_seconds": 30, "type": "polling"
                    },
                    "endpoint": API.SQLALCHEMY_DATABASE_URI  + "plugins/dropbox/status",
                    "data_type": "spot",
                    "logic": "boolean",
                    "field": {"response":"status"},
                    "field_type": "string",
                    "display_type": "list",
                    "detail_text_field": {'response': 'response'},
                },
                "enabled": 1
            },
            {
                "id": 3,
                "label": "facebook status",
                "width": "25%",
                "height": "100%",
                "data": {
                    "update_method": {
                        "interval_seconds": 30, "type": "polling"
                    },
                    "endpoint": API.SQLALCHEMY_DATABASE_URI  + "plugins/facebook/status",
                    "data_type": "spot",
                    "logic": "boolean",
                    "field": {"response":"status"},
                    "field_type": "string",
                    "display_type": "list",
                    "detail_text_field": {'response': 'response'},
                },
                "enabled": 1
            },
        ]
    }
]

# SQLAlchemy setup
Session = sessionmaker()
Base = declarative_base()


class _Role(Base):
    __tablename__ = "role"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(100), nullable=False, unique=True)
    description = sa.Column(sa.String(150), nullable=False)

    implicit_access = sa.Column(sa.Integer, default=_api_utils.UnixPermission.READ.value)
    super_admin = sa.Column(sa.Boolean, default=False)

class _User(Base):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)

    first_name = sa.Column(sa.String(50))
    last_name = sa.Column(sa.String(50))
    description = sa.Column(sa.String(255))

    email_address = sa.Column(sa.String(255), unique=True)
    password_hash = sa.Column(sa.String(255), nullable=False)
    active = sa.Column(sa.Boolean, nullable=False, default=False)

class _Group(Base):
    __tablename__ = "group"

    id = sa.Column(sa.Integer, primary_key=True)



def upgrade():
    test_dashboard

    binding = op.bind()
    session = Session(bind=binding)

    #session.add()
    _api_user_module_models.Role()

    session.add_all([
        _api_user_module_models.Role(
            name="root"
			description="Root user with superpowers.",
			super_admin=True,
			implicit_access=UnixPermission.ALL
        ),
    ])


#     insert the guest and root user
#
# session.add_all([
# 	Role(
# 		name="guest",
# 		description="Guest user with read-only permissions by default."
# 		implicit_access=UnixPermission.READ
# 	),
#
#
#
# ])


    #  insert the guest user dashboard




    session.commit()


def downgrade():

    binding = op.get_bind()
    session = Session(bind=binding)
    # remove above data

    session.commit()
