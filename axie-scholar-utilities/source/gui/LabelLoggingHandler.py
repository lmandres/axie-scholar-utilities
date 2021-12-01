import logging

from kivy.clock import Clock


# Code from: https://stackoverflow.com/a/34581893/4942592
class LabelLoggingHandler(logging.Handler):

    def __init__(self, label, level=logging.NOTSET):
        logging.Handler.__init__(self, level=level)
        self.label = label

    def emit(self, record):
        "using the Clock module for thread safety with kivy's main loop"
        def f(dt=None):
            self.label.text += "{}\n".format(self.format(record)) #"use += to append..."
        Clock.schedule_once(f, -1)