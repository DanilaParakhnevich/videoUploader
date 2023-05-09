class Settings(object):

    def __init__(self, language: str, download_strategy: int, autostart: bool, rate_limit: int,
                 download_dir: str, pack_count: int = 0):
        self.language = language
        self.download_strategy = download_strategy
        self.autostart = autostart
        self.download_dir = download_dir
        self.pack_count = pack_count
        self.rate_limit = rate_limit
