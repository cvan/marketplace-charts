#!/usr/bin/env python

import datetime
import json
import re

import webapp2
from google.appengine.api import urlfetch
from webapp2_extras import jinja2

from models.bug import Bug, ClosedBug, OpenedBug

PROJECTS = {
    'marketplace': {
        'opened': [
            ':marketplace creation_ts:{date}',
            ':marketplace delta_ts:{date} status:REOPENED'
        ],
        'closed': [
            'FIXED :marketplace delta_ts:{date}'
        ]
    }
}

# What we record in the DB.
BZ_MODEL_COLUMNS = (
    'product',
    'component',
    'id',
    'status',
    'resolution',
    'target_milestone',
    'summary',
    'assigned_to',
    'priority',
    'whiteboard'
)

# What we get back from Bugzilla.
BZ_FIELDS = (
    'id',
    'assigned_to',
    'priority',
    'summary',
    'status',
    'resolution',
    'last_change_time',
    'target_milestone',
    'whiteboard',
    'product',
    'component'
)

BZ_SEARCH_URL = ('https://api-dev.bugzilla.mozilla.org/latest/bug?'
                 'include_fields=%s&quicksearch=%%(qs)s') % ','.join(BZ_FIELDS)


class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, template, **context):
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)


class MainHandler(BaseHandler):

    def get(self):
        project = self.request.get('project', 'marketplace')
        if project not in PROJECTS:
            return

        # Two weeks of data.
        ctx = {'entries': reversed(
                   list(Bug.all().filter('project =', project)
                                 .order('-time')
                                 .run(limit=672)))}
        self.render_template('homepage.html', **ctx)


class BugsHandler(webapp2.RequestHandler):

    def _fetch_bugs(self, project, queries):
        today = datetime.date.today().strftime('%Y-%m-%d')
        for group_name, group_queries in queries.iteritems():
            for query in group_queries:
                url = (BZ_SEARCH_URL % {'qs': query}).format(date=today)
                #resp = urlfetch.fetch(url, headers={'Accept': 'application/json'})
                #content = resp.content
                #bugs = json.loads(content)
                bugs = []
                content = url
                self.response.write('<h1>For %s %s:</h1><p>%s</p>' % (group_name, url, content))

                # TODO: For reopened bugs, only insert if there is no record of the bug
                # or if there is a record of the bug its status was not previously 'REOPENED'.

                for bug in bugs:
                    if group_name == 'opened':
                        obj = OpenedBug
                    elif group_name == 'closed':
                        obj = ClosedBug

                    entry = obj(project=project, time=datetime.datetime.now())

                    for column in BZ_MODEL_COLUMNS:
                        setattr(entry, 'bz_' + column, bug[column])

                    entry = obj.put()

    def get(self):
        for k, v in PROJECTS.iteritems():
            self._fetch_bugs(k, v)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/tasks/bugs', BugsHandler),
], debug=True)
