class Channel(object):

    def __init__(self, hosting, url, login=None, password=None, auth=None, auth_data_lifetime=None):
        self.hosting = hosting
        self.url = url
        self.login = login
        self.password = password
        self.auth = auth
        self.authDataLifetime = auth_data_lifetime
