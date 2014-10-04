"""Publishes all OSC events, aliases most important events to a simpler name"""
import collections

import liblo

from ..utils.abstract_pub_sub_trans import EventPublisher

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
            self.provider.notify(self.path_alias(path), self.OSCEvent(t, a, path))

    def __init__(self, msg_center, port = 5001):
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
