from datetime import datetime
from yams_api.api import db
from sqlalchemy.ext.declarative import declared_attr

from enum import Enum
class UnixPermission(Enum):
    READ = 1
    WRITE = 2
    EXECUTE = 4
    NONE = 0
    READ_WRITE = READ + WRITE
    READ_EXECUTE = READ + EXECUTE
    ALL = READ + WRITE + EXECUTE


# display is currently:

# yamsPanel ~= row
#   inside a yamsPanel is a yamsBoxGroup
#       inside a yamsBoxGroup is N yamsBox

# yamsPanels/rows are ordered vertically.
# yamsBoxes are ordered positionally in their group "horizontally"

# a yamsBox is potentially many to many to a yamsBoxGroup  (if not, we'd have duplicate rows to present the same content).
# e.g. linking Github and AWS in 'deploy' group, or AWS and Netflix
yamsbox_yamsboxgroup_association = db.Table(
    'mapping_yams_box__yams_box_group',
    db.metadata,
    db.Column('yams_box_id', db.Integer, db.ForeignKey('yams_box.id')),
    db.Column('yams_box_group_id', db.Integer, db.ForeignKey('yams_box_group.id'))
)


class BaseDashboardUnit(db.Model):
    __abstract__ = True

    id =db.Column(db.Integer, primary_key=True, autoincrement=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    @declared_attr
    def owner_user_id(cls):
        return db.Column(db.Integer, db.ForeignKey("user.id"))

    @declared_attr
    def owner_group_id(cls):
        return db.Column(db.Integer, db.ForeignKey("group.id"))

    permission_user = db.Column(db.Enum(UnixPermission), default=UnixPermission.READ_WRITE)
    permission_group = db.Column(db.Enum(UnixPermission), default=UnixPermission.READ)
    permission_other = db.Column(db.Enum(UnixPermission), default=UnixPermission.NONE)

    # if the panel is private and there's a user_id, it shouldn't be available to other users
    user_id = db.Column("user_id", db.Integer, default=0)
    private = db.Column(db.Boolean, nullable=False, default=False)


class BaseDashboardUnitWithText(BaseDashboardUnit):
    __abstract__ = True

    name = db.Column(db.String(100))
    description = db.Column(db.String(255))


class yamsBoxPanel(BaseDashboardUnitWithText):
    __tablename__ = "yams_box_panel"

    # should simplify the isinstance checking in the code
    display_position = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return "<yamsBoxGroupPanel %r : %r %r>" % self.id, self.active, self.last_updated


class yamsBoxGroup(BaseDashboardUnitWithText):
    __tablename__ = "yams_box_group"

    # boxgroups are associated with a single yamsBoxGroupPanel
    yams_box_panel_id = db.Column(db.Integer, db.ForeignKey('yams_box_panel.id'))

    def __repr__(self):
        return "<yamsBoxGroup %r : %r %r>" % self.id, self.active, self.last_updated


class yamsBox(BaseDashboardUnitWithText):
    __tablename__ = "yams_box"

    # 25%....2500px, etc.
    display_width = db.Column(db.String(10))
    display_height = db.Column(db.String(10))
    display_position = db.Column(db.Integer)

    data_update_interval_seconds = db.Column(db.Integer, default=300)
    data_update_method_type= db.Column(db.String(50))  # e.g. polling, etc
    data_endpoint_path = db.Column(db.String(255))
    data_metric_type = db.Column(db.String(50))  # e.g. "spot" or "series"

    response_logic = db.Column(db.String(50))  # e.g. boolean for up/down
    response_search_path = db.Column(db.String(1000))
    response_search_path_datatype = db.Column(db.String(100))
    response_search_path_extended_detail = db.Column(db.String(1000))
    response_display_typehint = db.Column(db.String(100))  # e.g. "list" or "graph"

    # enabled = super().active

    def __repr__(self):
        return "<yamsBox %r : %r %r>" % self.id, self.active, self.last_updated
