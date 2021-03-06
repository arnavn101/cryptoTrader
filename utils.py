#!/usr/bin/python

from threading import Timer
import time


class RepeatedTimer(object):
    """
    Periodically executes the input function given the interval
    Source: https://stackoverflow.com/a/13151104/11761743
    """
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


def UnixTimeToLocal(unixTime):
    return time.strftime('%m-%d-%Y %H:%M:%S', time.localtime(int(unixTime)))


def percent_difference(new_value, original_value):
    return (new_value - original_value) / original_value
