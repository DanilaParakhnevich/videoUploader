class TabModel(object):

    def __init__(self, tab_name, channel, hosting, format, video_quality, remove_files_after_upload):
        self.tab_name = tab_name
        self.channel = channel
        self.hosting = hosting
        self.format = format
        self.video_quality = video_quality
        self.remove_files_after_upload = remove_files_after_upload