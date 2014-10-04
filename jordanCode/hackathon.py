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
import urllib2

host = "http://192.168.59.132:5000"

class OSCEventHandler:

    blink_event_time = 2
    seek_multiplyer = 5

    def blob_to_hex(self, b):
        return " ".join([ (hex(v/16).upper()[-1] + hex(v%16).upper()[-1]) for v in b ])

    def clenchEndEvent(self, event_time):
        clench_time = abs( event_time - self.data['clench_start_time'] )
        print("EVENT: Clench for " + str(clench_time) + " seconds")
        if clench_time > 1:
            seek_time = int(round(clench_time * self.seek_multiplyer))
            r = urllib2.urlopen(host + '/seek/' + str(seek_time))
        if self.data['last_clench_time'] and self.data['last_clench_time'] < 1 and clench_time < 1:
            self.sendPauseReq()
            self.data['last_clench_time'] = False
        else:
            self.data['last_clench_time'] = clench_time
        

    def sendPauseReq(self):
        r = urllib2.urlopen(host + '/pause_play')

    def blinkEvent(self, event_time):
        if not self.data['first_blink']:
            self.data['first_blink'] = event_time
            
            if self.data['blink_timer']:
                self.data['blink_timer'].cancel()
            self.data['blink_timer'] = threading.Timer(self.blink_event_time, self.blinkPeriodEnd).start()
            
            self.data['num_of_blinks_in_row'] = 1
        elif abs(event_time - self.data['first_blink']) <= self.blink_event_time:
            self.data['num_of_blinks_in_row'] += 1
        else:
            self.data['blink_timer'].cancel()
            if self.data['num_of_blinks_in_row'] > 1:
                self.blinksInARowEvent(self.data['num_of_blinks_in_row'])
            self.data['num_of_blinks_in_row'] = 0
            self.data['first_blink'] = None
        print("EVENT: Blink detected!")

    def blinkPeriodEnd(self):
        if self.data['num_of_blinks_in_row'] > 1:
            self.blinksInARowEvent(self.data['num_of_blinks_in_row'])
        self.data['num_of_blinks_in_row'] = 0
        self.data['first_blink'] = None
        self.data['blink_timer'] = None

    def blinksInARowEvent(self, num_of_blinks):
        print("EVENT: " + str(num_of_blinks) + " of blinks in a row!")
        if num_of_blinks >= 4:
            r = urllib2.urlopen(host + '/next_video')


    def callback(self, path, args, types, src):
        if ((path.find("jaw_clench") > -1) or (path.find("touching_forehead") > -1) or (path.find("blink") > 0)):
            write = sys.stdout.write
            ## print source
            #write("from " + src.get_url() + ": ")
            # print path
            #write(path + " ,")
            # print typespec
            #write(types)
            # loop through arguments and print them
            for a, t in zip(args, types):
                if t == None:
                    #unknown type
                    write("[unknown type]")
                elif t == 'b':
                    # it's a blob
                    write("[" + self.blob_to_hex(a) + "]")
                elif t == 'i':
                    #its an int
                    self.track_changes(path, a)
                    #write(str(a))
                else:
                   # anything else
                    #write(str(a))
                    pass
            #write('\n')

    def track_changes(self, path, value):
        if path.find("touching_forehead") > -1:
            if value == 1:
                self.data['touching_forehead'] = True
            else:
                self.data['touching_forehead'] = False
        if self.data['touching_forehead']:
            if path.find("jaw_clench") > -1:
                if value > 0 and self.data['clench_last_one']:
                    self.data['last_clench_streak'] += 1
                elif value > 0:
                    self.data['clench_start_time'] = time.time()
                    self.data['last_clench_streak'] = 1
                    self.data['clench_last_one'] = True
                elif self.data['clench_last_one']:
                    self.data['clench_last_one'] = False
                    self.clenchEndEvent(time.time())
            elif path.find("blink") > -1:
                if value > 0 and not self.data['blink_in_progress']:
                    self.data['blink_in_progress'] = True
                elif value == 0 and self.data['blink_in_progress']:
                    self.data['blink_in_progress'] = False
                    self.blinkEvent(time.time())


    def __init__(self, port = None):

        #init vars
        self.data = {}
        self.data['touching_forehead'] = False
        self.data['last_clench_streak'] = 0
        self.data['clench_start_time'] = None
        self.data['clench_last_one'] = False
        self.data['blink_in_progress'] = False
        self.data['first_blink'] = None
        self.data['num_of_blinks_in_row'] = 0
        self.data['blink_timer'] = None
        self.data['last_clench_time'] = None

        # create server object
        try:
            self.server = liblo.Server(port)
        except liblo.ServerError, err:
            sys.exit(str(err))

        print "listening on URL: " + self.server.get_url()

        # register callback function for all messages
        self.server.add_method(None, None, self.callback)

    def run(self):
        # just loop and dispatch messages every 10ms
        while True:
            self.server.recv(10)


if __name__ == '__main__':
    # display help
    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help"):
        sys.exit("Usage: " + sys.argv[0] + " port")

    # require one argument (port number)
    if len(sys.argv) < 2:
        sys.exit("please specify a port or URL")

    app = OSCEventHandler(sys.argv[1])
    try:
        app.run()
    except KeyboardInterrupt:
        del app
