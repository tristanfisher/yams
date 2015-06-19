from datetime import datetime
from yams_api.api import db

# try to use Flask-SQLAlchemy before heading down this path
#from sqlalchemy.ext.declarative import declarative_base
#Base = declarative_base()

class UnixPermission:
    READ = 1
    WRITE = 2
    EDIT = 4
    READ_WRITE = READ + WRITE
    ALL = READ + WRITE + EDIT


uid_gid_association = db.Table(
    'gid_uid_mapping',
    db.metadata,
    db.Column('uid', db.Integer, db.ForeignKey('user.id')),
    db.Column('gid', db.Integer, db.ForeignKey('group.id'))
)

class User(db.Model):
    __tablename__ = "user"

    _id = db.Column("id", db.Integer, primary_key=True)
    usercontact_id = db.relationship("UserContact", uselist=False, backref="user")

    password_hash = db.Column(db.String(255), nullable=False)

    active = db.Column(db.Boolean, nullable=False, default=False)
    super_admin = db.Column(db.Boolean, default=False)
    last_updated = db.Column("last_updated", db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return "<User %r : %r %r>" % self.id, self.first_name, self.last_name

class UserContact(db.Model):

    __tablename__ = "user_contact"

    _id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    first_name = db.Column(db.String(50), default="", unique=True)
    last_name = db.Column(db.String(50), default="", unique=True)
    description = db.Column(db.String(500))

    # string because ext. #
    phone_number = db.Column(db.String(50))
    skype_handle = db.Column(db.String(100))
    google_handle = db.Column(db.String(100))
    email_address = db.Column(db.String(200), unique=True)


class Group(db.Model):
    __tablename__ = "group"
    _id = db.Column("id", db.Integer, primary_key=True)
    uid = db.relationship("User", secondary=uid_gid_association, backref="group")

    active = db.Column(db.Boolean, nullable=False, default=False)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return "<Group %r : %r>" % self.id, self.name
