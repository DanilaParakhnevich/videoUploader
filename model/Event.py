import datetime


class Event(object):

    def __init__(self, msg):
        self.msg = msg
        self.date = datetime.datetime.now()
