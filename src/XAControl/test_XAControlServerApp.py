#!/usr/bin/python
# -*- coding: utf-8 -*-
from unittest import TestCase

from webtest import TestApp

from XAControl.XAControlServerApp import XAControlServerApp

__author__ = 'Marco Bartel'


class TestXAControlServerApp(TestCase):
    def setUp(self):
        self.app = XAControlServerApp()
        self.apiuser = "DOOR001"
        self.apikey = "AUALUON"

        self.testapp = TestApp(self.app.wsgiApp())
        self.testapp.authorization = ('Basic', (self.apiuser, self.apikey))



    def test_status_GET(self):
        res = self.testapp.get('/status', status=200)
        print res

