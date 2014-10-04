"""Provides abstract classes for the PubSub pattern, plus one for translator (both subs and pubs)"""
from abc import ABCMeta, abstractmethod

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