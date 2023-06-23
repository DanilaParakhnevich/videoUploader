from ffmpeg import FFmpeg

if __name__ == '__main__':
    ffmpeg = (FFmpeg(
        executable='/home/dendil/Documents/Projects/Own/BuxarVideoUploader/dist/Application/ffmpeg-master-latest-linux64-gpl/bin/ffmpeg')
              .input('/home/dendil/Desktop/Личное/Youtube/Еду как хочу и на других насрать. Гос номер АК8198-4._720.mp4')
              .option('y')
              .output('/home/dendil/Desktop/Личное/Youtube/Еду как хочу и на других насрать. Гос номер АК8198-4._721.mp4')
              )
    ffmpeg.execute()