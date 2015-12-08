#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
import cherrypy
from cherrypy.process import bus
import zope.interface

__author__ = 'Marco Bartel'

class WSGIServer(threading.Thread):
    def __init__(self, app=None, port=None, threads=5, cert='cert/develop_cert.pem', key='cert/develop_priv.pem', logScreen=False):
        threading.Thread.__init__(self)
        self.daemon = True
        self.logScreen = logScreen
        self.app = app
        self.port = port
        self.threads = threads
        self.cert = cert
        self.key = key

        self.config = {
            'engine.autoreload.on': False,
            'log.screen': self.logScreen,
            'server.socket_host': "0.0.0.0",
            'server.thread_pool': self.threads,
            # 'server.socket_port': 80,

            # For SSL Support
            'server.socket_port': self.port,
            # 'server.ssl_module': 'pyopenssl',
            # 'server.ssl_certificate': self.cert,
            # 'server.ssl_private_key': self.key,
            'tools.sessions.on': True,
            # 'server.ssl_certificate_chain': 'ssl/bundle.crt'
        }


    def run(self):
        cherrypy.config.update(self.config)
        self.wsgi = self.app.wsgiApp()
        # Mount the application (or *app*)
        cherrypy.tree.graft(self.wsgi, "/")
        cherrypy.engine.start()
        cherrypy.engine.block()
        print "This is the end of port %s....." % self.port


    def exit(self):
        print "call exit"
        cherrypy.engine.exit()
