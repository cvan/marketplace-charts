from google.appengine.ext import db


class Bug(db.Model):
    project = db.StringProperty(required=True)
    bz_product = db.StringProperty(required=True)
    bz_component = db.StringProperty(required=True)
    bz_number = db.StringProperty(required=True)
    bz_status = db.StringProperty(required=True)
    bz_resolution = db.StringProperty(required=False)
    bz_description = db.StringProperty(required=False)
    bz_milestone = db.StringProperty(required=False)
    bz_assignee = db.StringProperty(required=False)
    bz_priority = db.StringProperty(required=False)
    bz_whiteboard = db.StringProperty(required=False)
    custom_component = db.StringProperty(required=False)
    time = db.DateTimeProperty(required=True)


class OpenedBug(Bug):
    """A NEW or REOPENED bug."""


class ClosedBug(Bug):
    """A RESOLVED bug."""