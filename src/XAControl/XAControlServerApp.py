#!/usr/bin/python
# -*- coding: utf-8 -*-
import binascii
import os
import re

import psutil
from pyramid.config import Configurator
from pyramid.request import Request
# noinspection PyUnresolvedReferences
from paste.httpheaders import AUTHORIZATION
import XACPifaceRelayPlus
from RestService import RestService, RestServiceObject

__author__ = 'Marco Bartel'


class XAControlServerRequest(Request):
    restServer = None

    def __init__(self, environ, charset=None, unicode_errors=None, decode_param_names=None, **kw):
        super(XAControlServerRequest, self).__init__(environ, charset, unicode_errors, decode_param_names, **kw)
        if XAControlServerApp.debug:
            print "HOST:", self.client_addr, "ACCESS:", self.url

    def check_auth(self):
        self.credentials = self.getBasicauthCredentials()
        if not self.credentials:
            self.response.status = 403
        else:
            if not self.restServer.checkRestAccess(self.credentials):
                self.response.status = 403
            else:
                self.response.status = 200

        return

    def getBasicauthCredentials(self):
        authorization = AUTHORIZATION(self.environ)
        try:
            authmeth, auth = authorization.split(' ', 1)
        except ValueError:  # not enough values to unpack
            return None

        if authmeth.lower() == 'basic':
            try:
                auth = auth.strip().decode('base64')
            except binascii.Error:  # can't decode
                return None
            try:
                login, password = auth.split(':', 1)
            except ValueError:  # not enough values to unpack
                return None
            return {'login': login, 'password': password}

        return None


class XAControlServerApp(object):
    testing = False
    debug = True
    validKeyCache = {"DOOR001": "AUALUON"}
    operators = {}

    def __init__(self):
        RestServiceObject.server = self
        self.setupApp()
        # self.clearOperators()

    def setupApp(self):
        XAControlServerRequest.restServer = self

        self.config = Configurator()
        self.config.set_request_factory(XAControlServerRequest)

        for method in RestService.services:
            for route in RestService.services[method]:
                obj = RestService.services[method][route]
                name = str(frozenset((method, route)))
                print "registering %6s '%s' " % (method, route)
                self.config.add_route(name, route)
                self.config.add_view(obj.call, request_method=method, route_name=name, renderer='json')

    def checkRestAccess(self, credentials):
        apiuser = credentials["login"]
        apikey = credentials["password"]
        if not apiuser in self.validKeyCache:
            return False
        else:
            return True if self.validKeyCache[apiuser] == apikey else False

    def wsgiApp(self):
        return self.config.make_wsgi_app()

    @staticmethod
    @RestService("/status")
    def status_GET(request=None, server=None):

        ownPID = os.getpid()
        ownProcessInfo = psutil.Process(ownPID)
        try:
            ownMemoryUsage = ownProcessInfo.memory_info()[0]
        except:
            ownMemoryUsage = ownProcessInfo.get_memory_info()[0]
        return {
            "MEMORY_USAGE": ownMemoryUsage,
        }
