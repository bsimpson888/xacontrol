#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

__author__ = 'Marco Bartel'

class RestServiceObject(object):
    parameterRegex = re.compile(ur'\{(.*?)\}')
    server = None

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

            return self.callFunc(request=request, server=self.server, **kwargs)


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