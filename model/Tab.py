class TabModel(object):

    def __init__(self, tab_name, channel, hosting, format, video_quality, video_extension, remove_files_after_upload, download_dir,
                 manual_settings=True, video_quality_str=0, video_bitrate=0, audio_quality_str=0, audio_bitrate=0, audio_sampling_rate=0,
                 fps=0, current_channel=None):
        self.tab_name = tab_name
        self.channel = channel
        self.hosting = hosting
        self.format = format
        self.video_quality = video_quality
        self.video_extension = video_extension
        self.remove_files_after_upload = remove_files_after_upload
        self.download_dir = download_dir
        self.video_list = list()
        self.manual_settings = manual_settings
        self.video_quality_str = video_quality_str
        self.video_bitrate = video_bitrate
        self.audio_quality_str = audio_quality_str
        self.audio_bitrate = audio_bitrate
        self.audio_sampling_rate = audio_sampling_rate
        self.fps = fps
        self.current_channel = current_channel
