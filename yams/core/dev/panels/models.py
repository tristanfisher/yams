from datetime import datetime
from yams.app import db


class UnixPermission:
    READ = 1
    WRITE = 2
    EDIT = 4
    READ_WRITE = READ + WRITE
    ALL = READ + WRITE + EDIT


class Panel(db.Model):

    __tablename__ = "panel"

    _id = db.Column("id", db.Integer)

    # todo: this should associate with the auth session somehow.
    # if the panel is private and there's a user_id, it shouldn't be available to other users
    user_id = db.Column("user_id", db.Integer, default=0)
    private = db.Column(db.Boolean, nullable=False, default=False)

    active = db.Column(db.Boolean, nullable=False, default=True)
    last_updated = db.Column("last_updated", db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return "<Panel %r : %r %r>" % self.id, self.active, self.last_updated
