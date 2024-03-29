from google.appengine.ext import db
from google.appengine.ext.db import polymodel


class Bug(polymodel.PolyModel):
    project = db.StringProperty(required=True)
    bz_product = db.StringProperty(required=True)
    bz_component = db.StringProperty(required=True)
    bz_id = db.IntegerProperty(required=True)
    bz_status = db.StringProperty(required=True)
    bz_summary = db.StringProperty(required=False)
    bz_target_milestone = db.StringProperty(required=False)
    bz_assigned_to = db.StringProperty(required=False)
    bz_priority = db.StringProperty(required=False)
    bz_whiteboard = db.StringProperty(required=False)
    bz_creation_ts = db.StringProperty(required=False)
    bz_last_change_time = db.StringProperty(required=False)
    custom_component = db.StringProperty(required=False)
    time = db.DateTimeProperty(required=True)


class OpenedBug(Bug):
    """A NEW or REOPENED bug."""


class ClosedBug(Bug):
    """A RESOLVED bug."""
    bz_resolution = db.StringProperty(required=False)
