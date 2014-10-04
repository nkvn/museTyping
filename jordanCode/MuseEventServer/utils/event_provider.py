"""Queues and dispatches messages to subcribers"""
import collections

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
        if key not in self.subcribers:
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
