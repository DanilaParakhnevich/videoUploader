class Channel(object):

    def __init__(self, hosting=None, url=None, login=None, password=None, session=None):
        self.hosting = hosting
        self.url = url
        self.login = login
        self.password = password
        self.session = session

