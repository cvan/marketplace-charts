#!/usr/bin/env python

import datetime
import re

import webapp2
from google.appengine.api import urlfetch
from webapp2_extras import jinja2

from models.entry import Entry

projects = {
    'marketplace': {
        'opened': [
            ':marketplace creation_ts:%(date)s',
            ':marketplace delta_ts:%(date)s status:REOPENED'
        ],
        'closed': [
            'FIXED :marketplace delta_ts:%(date)s'
        ]
    }
}


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
        if project not in projects:
            return

        # Two weeks of data.
        ctx = {'entries': reversed(
                   list(Entry.all().filter('project =', project)
                                   .order('-time')
                                   .run(limit=672)))}
        self.render_template('homepage.html', **ctx)


class BugsHandler(webapp2.RequestHandler):

    def _fetch_bugs(self, project, queries):
        # TODO: Scrape bugzill and save objects.
        pass

    def get(self):
        for k, v in projects.iteritems():
            self._fetch_bugs(k, v)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/tasks/bugs', BugsHandler),
], debug=True)
