# coding=utf-8
from __future__ import unicode_literals, absolute_import
from flask.ext.script import Command
import celery

__all__ = ["Celery"]

__version__ = "0.1.4"
__author__ = "webee.yw"
__license__ = "MIT"
__description__ = "extras commands to Flask-Script."
__uri__ = "https://github.com/webee/flask-script-extras"
__email__ = "webee.yw@gmail.com"


class Celery(Command):
    """execute celery"""

    def __init__(self, celery_app):
        self.celery_app = celery_app
        self.capture_all_args = True

    def _get_celery_app(self):
        if isinstance(self.celery_app, celery.Celery):
            return self.celery_app
        elif isinstance(self.celery_app, (str, unicode)):
            mod_path, app_name = map(str, self.celery_app.split(':'))
            return getattr(__import__(mod_path, fromlist=[mod_path]), app_name)
        else:
            raise NotImplementedError('type not supported: {0}.'.format(type(self.celery_app)))

    def run(self, *args, **kwargs):
        self._get_celery_app().start(argv=['celery'] + args[0])
