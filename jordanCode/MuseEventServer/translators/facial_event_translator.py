import time
import threading

from ..utils.abstract_pub_sub_trans import EventTranslator

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
        for k in self.msg_keys_handled:
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
