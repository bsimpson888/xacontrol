#!/usr/bin/python
# -*- coding: utf-8 -*-
import binascii
import datetime
import os
import re
import threading
import uuid

import psutil
from pyramid.config import Configurator
from pyramid.request import Request
# noinspection PyUnresolvedReferences
from paste.httpheaders import AUTHORIZATION

__author__ = 'Marco Bartel'


class RestServiceObject(object):
    parameterRegex = re.compile(ur'\{(.*?)\}')

    def __init__(self, method=None, route=None, callFunc=None):
        self.method = method
        self.route = route
        self.routeParameters = []
        rp = self.parameterRegex.findall(self.route)
        for p in rp:
            psplitted = p.split(":")
            if len(psplitted) == 2:
                self.routeParameters.append((psplitted[0], eval(psplitted[1])))
                self.route = self.route.replace("{p}".format(p=p), "{p}".format(p=psplitted[0]))
            else:
                self.routeParameters.append((psplitted[0], unicode))

        self.callFunc = callFunc
        if self.method not in RestService.services:
            RestService.services[self.method] = {}
        RestService.services[self.method][self.route] = self

    def call(self, context, request, **kwargs):
        request.check_auth()
        if request.response.status_code == 200:
            for (pname, ptype) in self.routeParameters:
                try:
                    kwargs[pname] = ptype(request.matchdict[pname])
                except ValueError:
                    return {"ERROR": "BAD PARAMETERS"}

            return self.callFunc(request=request, **kwargs)


class RestService(object):
    services = {}

    def __init__(self, route):
        self.route = route

    def __call__(self, func):
        restServiceObj = RestServiceObject(
            method=func.__name__.split("_")[-1].upper(),
            route=self.route,
            callFunc=func
        )

        def inner(**kwargs):
            restServiceObj.call(**kwargs)

        return inner



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
    debug = True
    validKeyCache = {"DOOR001": "AUALUON"}
    operators = {}

    def __init__(self):

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
    def status_GET(request=None):

        ownPID = os.getpid()
        ownProcessInfo = psutil.Process(ownPID)
        try:
            ownMemoryUsage = ownProcessInfo.memory_info()[0]
        except:
            ownMemoryUsage = ownProcessInfo.get_memory_info()[0]
        return {
            "MEMORY_USAGE": ownMemoryUsage,
        }

