#!/usr/bin/python
# -*- coding: utf-8 -*-
from unittest import TestCase

import time
from webtest import TestApp
from XAControl.XAControlServerApp import XAControlServerApp

__author__ = 'Marco Bartel'


class TestXAControlServerApp(TestCase):
    def setUp(self):
        XAControlServerApp.testing = True
        self.app = XAControlServerApp()
        self.apiuser = "DOOR001"
        self.apikey = "AUALUON"

        self.testapp = TestApp(self.app.wsgiApp())
        self.testapp.authorization = ('Basic', (self.apiuser, self.apikey))

    def test_status_GET(self):
        res = self.testapp.get('/status', status=200)
        self.assertTrue("MEMORY_USAGE" in res.json)


    def test_relay_POST(self):
        CHANNEL = 0
        STATE = 1
        res = self.testapp.post(
            '/relay/{CHANNEL}/{STATE}'.format(
                CHANNEL=CHANNEL,
                STATE=STATE
            ),
            status=200
        )
        time.sleep(1)
        STATE = 0
        res = self.testapp.post(
            '/relay/{CHANNEL}/{STATE}'.format(
                CHANNEL=CHANNEL,
                STATE=STATE
            ),
            status=200
        )
