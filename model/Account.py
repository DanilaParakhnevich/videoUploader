class Account(object):

    def __init__(self, hosting, login=None, password=None, auth=None, auth_data_lifetime=None):
        self.hosting = hosting
        self.login = login
        self.password = password
        self.auth = auth
        self.authDataLifetime = auth_data_lifetime
