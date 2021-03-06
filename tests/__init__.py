from __future__ import with_statement
import hmac
from hashlib import sha1
from unittest import TestCase
from flask import request, render_template
from flask_anyform import AnyForm, AForm
from wtforms import Form, TextField
from .test_app import create_app


class AnyFormTest(TestCase):
    APP_KWARGS = {}
    ANYFORM_CONFIG = None

    def setUp(self):
        super(AnyFormTest, self).setUp()

        class TestForm(Form):
            test = TextField(default='TEST FORM')

        class TestForm2(Form):
            test = TextField(default='TEST FORM TWO')

        self.forms = [
            {'af_tag':'test',
             'af_form': TestForm,
             'af_template': 'macros/_test.html',
             'af_macro': 'test_macro',
             'af_points': ['all'] },
            {'af_tag':'test2',
             'af_form': TestForm2,
             'af_template': 'macros/_test.html',
             'af_macro': 'test_macro',
             'af_points': ['notindex']}
        ]

        app_kwargs = self.APP_KWARGS
        app = self._create_app(self.ANYFORM_CONFIG or {}, **app_kwargs)
        app.debug = False
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = B'SECRET_KEY'
        app.anyform_e = AnyForm(app, forms=self.forms)

        self.app = app
        self.client = app.test_client()

        s = app.extensions['anyform']

        @s.aform_ctx
        def anyform_ctxfn():
            return {'t1val': "RETURNED FROM A FORM CONTEXT FUNCTION"}

        @s.aform_ctx
        def test2_ctxfn():
            return dict(t2v="RETURNED FROM A TAGGED CONTEXT VALUE FUNCTION")

        with self.client.session_transaction() as session:
            session['csrf'] = 'csrf_token'

        csrf_hmac = hmac.new(self.app.config['SECRET_KEY'], 'csrf_token'.encode('utf-8'), digestmod=sha1)
        self.csrf_token = '##' + csrf_hmac.hexdigest()

    def _create_app(self, anyform_config, **kwargs):
        return create_app(anyform_config, **kwargs)

    def _get(self,
            route,
            content_type=None,
            follow_redirects=None,
            headers=None):
        return self.client.get(route,
                            follow_redirects=follow_redirects,
                            content_type=content_type or 'text/html',
                            headers=headers)

    def _post(self,
            route,
            data=None,
            content_type=None,
            follow_redirects=True,
            headers=None):
        if isinstance(data, dict):
            data['csrf_token'] = self.csrf_token

        return self.client.post(route,
                            data=data,
                            follow_redirects=follow_redirects,
                            content_type=content_type or
                            'application/x-www-form-urlencoded',
                            headers=headers)
