from datetime import datetime
from yams_api.api import db
from yams_api.core.dev.utils import UnixPermission, unix_permission_list

# try to use Flask-SQLAlchemy before heading down this path:
#from sqlalchemy.ext.declarative import declarative_base
#Base = declarative_base()

# users have multiple groups, groups can have multiple people
uid_gid_association = db.Table(
    'mapping_user_group',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

# groups can have multiple roles, permissions have multiple groups
gid_rid_association = db.Table(
    'mapping_group_role',
    db.metadata,
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class BaseUser(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)
    time_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# keep simple for now, but i imagine there could be a point in maintaining a role to function mapping
# e.g. sysops [rw] -> aws rds,
class Role(BaseUser):
    __tablename__ = "role"

    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(150), nullable=False)

    # if not otherwise stated on the target resource. e.g. monitoring users would be implicit UnixPermission.READ
    # this is here to act like a mask -- so we can prevent a "demo users" Role from being able to write changes to
    # and endpoint that someone forgot to lock down.
    # mysql doesn't support checkconstraints, so just use int.
    implicit_access = db.Column(db.Integer, default=UnixPermission.READ.value)
    super_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Role %r>' % self.name


class User(BaseUser):
    __tablename__ = "user"

    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    description = db.Column(db.String(255))

    # string because ext. #
    phone_number = db.Column(db.String(100))
    skype_handle = db.Column(db.String(100))
    google_handle = db.Column(db.String(100))
    email_address = db.Column(db.String(255), unique=True)

    password_hash = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return "<User %r : %r %r>" % self.id, self.email_address, self.active


class Group(BaseUser):
    __tablename__ = "group"

    active = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return "<Group %r : %r>" % self.id, self.name