# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import pdb
for attr in ('stdin', 'stdout', 'stderr'):
    setattr(sys, attr, getattr(sys, '__%s__' % attr))

import datetime
import json
import re
import urllib2

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

# What we get back from Bugzilla. And what we record in the DB.
BZ_FIELDS = (
    'product',
    'component',
    'id',
    'assigned_to',
    'priority',
    'summary',
    'status',
    'resolution',
    #'last_change_time',
    'target_milestone',
    'whiteboard',
    'creation_ts'
)


BZ_TRANSFORMS = {
    'id': lambda x: int(x),
    'assigned_to': lambda x: x.get('real_name', x)
}



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
        ctx = {
            'entries': reversed(list(Bug.all().filter('project =', project)
                                        .order('-time')
                                        .run(limit=672))),
            # TODO: Group by day.
            'opened': list(OpenedBug.all()),
            'closed': list(ClosedBug.all())
        }
        self.render_template('homepage.html', **ctx)


class BugsHandler(webapp2.RequestHandler):

    def _fetch_bugs(self, project, queries):
        today = datetime.date.today().strftime('%Y-%m-%d')
        # TODO: The datetime is ahead by like a day. Figure out WTS is going on.
        today = '2012-12-19'
        self.response.write(today)
        for group_name, group_queries in queries.iteritems():

            # Depending on the group, pick a model.

            # TODO: Figure out why everything is getting saved as just a Bug.
            if group_name == 'opened':
                obj = OpenedBug
            elif group_name == 'closed':
                obj = ClosedBug

            for query in group_queries:
                url = BZ_SEARCH_URL % {'qs': urllib2.quote(query.format(date=today))}
                resp = urlfetch.fetch(url, headers={'Accept': 'application/json'})
                content = resp.content

                if not content:
                    return

                bugs = json.loads(content)['bugs']
                self.response.write('<h1>For %s %s</h1><p>%s</p>' % (group_name, url, bugs))

                # TODO: For reopened bugs, only insert if there is no record of the bug
                # or if there is a record of the bug its status was not previously 'REOPENED'.

                for bug in bugs:
                    props = {'project': project, 'time': datetime.datetime.now()}

                    for column in BZ_FIELDS:
                        if column in bug:
                            # Do field manipulations on a case-by-case basis.
                            if column in BZ_TRANSFORMS:
                                bug[column] = BZ_TRANSFORMS[column](bug[column])
                            props['bz_' + column] = bug[column]

                    # TODO: Do a `get_or_insert`.
                    obj(**props).put()

    def get(self):
        for project, queries in PROJECTS.iteritems():
            self._fetch_bugs(project, queries)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/tasks/bugs', BugsHandler),
], debug=True)
