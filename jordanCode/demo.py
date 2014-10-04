#!/usr/bin/env python2.7
"""MuseIC EventServer Demo Runner"""
import sys

from MuseEventServer.utils import event_provider
from MuseEventServer.subscribers.youtube_player_remote import YoutubePlayerRemote
from MuseEventServer.publishers.osc_event_publisher import OSCEventPublisher
from MuseEventServer.translators.facial_event_translator import FacialEventTranslator

__author__ = "Jordan Pryde"
__copyright__ = "Copyright 2014, Jordan Pryde"
__credits__ = ["Jordan Pryde", "Shirley Miao", "Athul Paul Jacob",
                    "Pritham"]
__license__ = "MIT"
__version__ = "0.2.0"
__maintainer__ = "Jordan Pryde"
__email__ = "jordan@pryde.me"
__status__ = "experimental"

if __name__ == '__main__':
    # display help
    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help"):
        sys.exit("Usage: " + sys.argv[0] + " port")

    # require one argument (port number)
    if len(sys.argv) < 2:
        sys.exit("please specify a port or socket path")

    msg_center = event_provider.EventProvider()
    osc_receiver = OSCEventPublisher(msg_center, port=sys.argv[1])
    fe_trans = FacialEventTranslator(msg_center)
    
    app = YoutubePlayerRemote(msg_center)  

    try:
        osc_receiver.run()
    except KeyboardInterrupt:
        del osc_receiver
