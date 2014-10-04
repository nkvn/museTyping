#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# pyliblo - Python bindings for the liblo OSC library
#
# Copyright (C) 2007-2011  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import sys
import liblo
import time
import threading
import urllib3
import collections

from abc import ABCMeta, abstractmethod

class YoutubePlayerRemote(EventSubscriber):

    def __init__(self, msg_center, host, port, secure):
        super(YoutubePlayerRemote, self).__init__(msg_center)

        self.host = host or '192.168.59.132'
        self.port = port or 5000
        self.secure = secure or False

        if self.secure:
            self.base_url = "https://"
        else:
            self.base_url = "http://"
        self.base_url += host + ":" + str(port)
        self.http = urllib3.PoolManager()

        self._get_subscriptions()

    def _get_subscriptions(self):
        msg_keys_handled = ['quick_clench_two_row',
                            'long_clench_rounded_int',
                            'blinks_in_a_row']
        for k in msg_keys_handled:
            self.subscribe(k)

    def subscribe(self, key):
        super(YoutubePlayerRemote, self).subscribe(key)

    def receive(self, key, payload):
        if key == 'quick_clench_two_row':
            self.sendPauseReq()
        elif key == 'long_clench_rounded_int':
            self.sendSeekReq(payload)
        elif (key == 'blinks_in_a_row') and (payload >= 4):
            self.sendPlaylistSkip()

    def sendReq(self, endpoint):
        r = self.http.request('GET', self.base_url + endpoint)
        if r.status != 200:
            raise sendError("Something went wrong with the Youtube remote server.")

    def sendPauseReq(self):
        self.sendReq('/pause_play')

    def sendSeekReq(self, seek_time):
        self.sendReq('/seek/' + str(seek_time))

    def sendPlaylistSkip(self):
        self.sendReq('/next_video')

class SendError(Exception):
    pass

class EventProvider:
    """Stores msgs and subcribers for generic events"""

    # makes thinks look a little nicer
    Msg = collections.namedtuple('Msg', ['key', 'payload'])

    def __init__(self):
        self.msg_queue = []
        self.subcribers = {}

    def notify(self, key, payload):
        msg = Msg(key, payload)
        self.msg_queue.append(msg)

    def subscribe(self, key, subcriber):
        if msg_key not in self.subcribers:
            self.subcribers[key] = []
            self.subcribers[key].append(subcriber)
        else:
            self.subcribers[key].append(subcriber)

    def unsubscribe(self, msg_key, subcriber):
        self.subcribers[msg_key].remove(subcriber)

    def update(self):
        for msg in self.msg_queue:
            if msg.key in self.subcribers:
                for sub in self.subcribers[msg.key]:
                    sub.receive(msg.key, msg.payload)
        self.msg_queue = []


class EventPublisher:
    """An abstract class that contains all the methods that others can depend upon a publisher to have"""
    __metaclass__ = ABCMeta

    def __init__(self, msg_center):
        self.provider = msg_center

    @abstractmethod
    def publish(self, key, payload):
        self.provider.notify(key, payload)


class EventSubscriber:
    """An abstract class that contains all the methods that others can depend upon a subscriber to have"""
    __metaclass__ = ABCMeta

    def __init__(self, msg_center):
        self.provider = msg_center

    @abstractmethod
    def subscribe(self, key):
        self.provider.subscribe(key, self)

    @abstractmethod
    def receive(self, key, payload): pass

class EventTranslator:
    """An abstract class that contains all the methods that others can depend upon a translator to have"""
    __metaclass__ = ABCMeta

    def __init__(self, msg_center):
        self.provider = msg_center

    @abstractmethod
    def publish(self, key, payload):
        self.provider.notify(key, payload)

    @abstractmethod
    def subscribe(self, key):
        self.provider.subscribe(key, self)

    @abstractmethod
    def receive(self, key, payload): pass



class FacialEventTranslator(EventTranslator):

    msg_keys_handled = ['OSC_jaw_clench', 'OSC_touching_forehead', 'OSC_blink']

    # Facial event params
    blink_event_time = 2
    seek_multiplyer = 5

    def __init__(self, msg_center):
        super(FacialEventTranslator, self).__init__(msg_center)

        # instance vars
        self.touching_forehead = False
        self.last_clench_streak = 0
        self.clench_start_time = None
        self.clench_last_one = False
        self.blink_in_progress = False
        self.first_blink = None
        self.num_of_blinks_in_row = 0
        self.blink_timer = None
        self.last_clench_time = None

        # Subscribe to events
        for k in msg_keys_handled:
            self.subscribe(k)

    def publish(self, key, payload):
        super(FacialEventTranslator, self).publish(key, payload)

    def subscribe(self, key):
        super(FacialEventTranslator, self).subscribe(key)

    def receive(self, key, payload):
        value = payload

        if key == 'OSC_touching_forehead':
            if value == 1:
                self.touching_forehead = True
            else:
                self.touching_forehead = False

        if self.touching_forehead:
            if key == 'OSC_jaw_clench':
                if value > 0 and self.clench_last_one:
                    self.last_clench_streak += 1
                elif value > 0:
                    self.clench_start_time = time.time()
                    self.last_clench_streak = 1
                    self.clench_last_one = True
                elif self.clench_last_one:
                    self.clench_last_one = False
                    self.clenchEndEvent(time.time())
            elif key == 'OSC_blink':
                if value > 0 and not self.blink_in_progress:
                    self.blink_in_progress = True
                elif value == 0 and self.blink_in_progress:
                    self.blink_in_progress = False
                    self.blinkEvent(time.time())


    def clenchEndEvent(self, event_time):
        clench_time = abs( event_time - self.clench_start_time )
        print("EVENT: Clench for " + str(clench_time) + " seconds")
        self.publish('clench_end', clench_time)
        if clench_time > 1:
            rounded_int = int(round(clench_time * self.seek_multiplyer))
            self.publish('long_clench_rounded_int', rounded_int)

        if self.last_clench_time and self.last_clench_time < 1 and clench_time < 1:
            self.publish('quick_clench_two_row', clench_time)
            self.last_clench_time = False
        else:
            self.last_clench_time = clench_time


    def blinkEvent(self, event_time):
        self.publish('blink', None)
        if not self.first_blink:
            self.first_blink = event_time

            if self.blink_timer:
                self.blink_timer.cancel()
            self.blink_timer = threading.Timer(self.blink_event_time, self.blinkPeriodEnd).start()

            self.num_of_blinks_in_row = 1
        elif abs(event_time - self.first_blink) <= self.blink_event_time:
            self.num_of_blinks_in_row += 1
        else:
            self.blink_timer.cancel()
            if self.num_of_blinks_in_row > 1:
                self.blinksInARowEvent(self.num_of_blinks_in_row)
            self.num_of_blinks_in_row = 0
            self.first_blink = None
        print("EVENT: Blink detected!")

    def blinkPeriodEnd(self):
        self.publish('blink_period_end')
        if self.num_of_blinks_in_row > 1:
            self.blinksInARowEvent(self.num_of_blinks_in_row)
        self.num_of_blinks_in_row = 0
        self.first_blink = None
        self.blink_timer = None

    def blinksInARowEvent(self, num_of_blinks):
        print("EVENT: " + str(num_of_blinks) + " of blinks in a row!")
        self.publish('blinks_in_a_row', num_of_blinks)


class OSCEventPublisher(EventPublisher):
    """Grabs all the OSCEvents then publishes the events to the msg_center"""
    msg_center = None

    event_aliases = {'/muse/dsp/elements/jaw_clench': 'OSC_jaw_clench',
                     '/muse/dsp/elements/touching_forehead': 'OSC_touching_forehead',
                     '/muse/dsp/blink': 'OSC_blink'}

    OSCEvent = collections.namedtuple('OSCEvent', ['type', 'payload', 'raw_path'])

    def path_alias(self, path):
        if path in self.event_aliases:
            return self.event_aliases[path]
        else:
            return path

    def publish(self, key, payload):
        super(OSCEventPublisher, self).publish(key, payload)

    def callback(self, path, args, types, src):
        for t, a in zip(types, args):
            self.provider.notify(path_alias(path), OSCEvent(t, a, path))

    def __init__(self, port = None, msg_center):
        super(OSCEventPublisher, self).__init__(msg_center)

        # create server object
        try:
            self.server = liblo.Server(port)
        except liblo.ServerError, err:
            sys.exit(str(err))

        print "listening on URL: " + self.server.get_url()

        # get the fire hose
        self.server.add_method(None, None, self.callback)

    def run(self):
        # just loop and dispatch messages every 10ms
        while True:
            self.server.recv(10)
            self.provider.update()


if __name__ == '__main__':
    # display help
    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help"):
        sys.exit("Usage: " + sys.argv[0] + " port")

    # require one argument (port number)
    if len(sys.argv) < 2:
        sys.exit("please specify a port or socket path")

    app = OSCEventHandler(sys.argv[1], FacialEventReceiver)
    try:
        app.run()
    except KeyboardInterrupt:
        del app
