"""Sends commands to a YouTube remote server (see MuseIC-YouTubeDemo)"""
import urllib3

from ..utils.abstract_pub_sub_trans import EventSubscriber

class YoutubePlayerRemote(EventSubscriber):

    def __init__(self, msg_center, host=None, port=None, secure=False):
        super(YoutubePlayerRemote, self).__init__(msg_center)

        self.host = host or '192.168.59.132'
        self.port = port or 5000
        self.secure = secure or False

        if self.secure:
            self.base_url = "https://"
        else:
            self.base_url = "http://"
        self.base_url += self.host + ":" + str(self.port)
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
