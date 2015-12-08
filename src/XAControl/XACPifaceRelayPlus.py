#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading

import pifacerelayplus

from XAControl.RestService import RestService

__author__ = 'Marco Bartel'


class XACPifaceRelayPlus(object):
    pfr = pifacerelayplus.PiFaceRelayPlus(pifacerelayplus.RELAY)
    lock = threading.Lock()

    @staticmethod
    @RestService("/relay/{CHANNEL:int}/{STATE:int}")
    def relay_POST(request=None, server=None, CHANNEL=None, STATE=None):
        if server.testing:
            print "relay_POST Channel", CHANNEL, "State", STATE
        else:
            XACPifaceRelayPlus.lock.acquire()
            XACPifaceRelayPlus.pfr.relays[CHANNEL].value = STATE
            XACPifaceRelayPlus.lock.release()
        return {}
