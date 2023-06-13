import os
from http.cookiejar import Cookie

from youtube_dl import YoutubeDL

if __name__ == '__main__':
    download_video_opts = {
        'ffmpeg_location': os.path.abspath('dist/Application/ffmpeg-master-latest-linux64-gpl/bin'),
        'ignoreerrors': True,
    }

    with YoutubeDL(download_video_opts) as ydl:
        for auth in [{'name': 'datr', 'value': 'rkOCZKcmlCHAIDhfGgJlweTa', 'domain': '.facebook.com', 'path': '/',
                      'expires': 1720818606.719527, 'httpOnly': True, 'secure': True, 'sameSite': 'None'},
                     {'name': 'sb', 'value': 'rkOCZNSXkO7-ammRxIcJN43R', 'domain': '.facebook.com', 'path': '/',
                      'expires': 1720818628.835623, 'httpOnly': True, 'secure': True, 'sameSite': 'None'},
                     {'name': 'locale', 'value': 'en_GB', 'domain': '.facebook.com', 'path': '/',
                      'expires': 1686863409.527695, 'httpOnly': False, 'secure': True, 'sameSite': 'None'},
                     {'name': 'c_user', 'value': '100092379542437', 'domain': '.facebook.com', 'path': '/',
                      'expires': 1717794624.835659, 'httpOnly': False, 'secure': True, 'sameSite': 'None'},
                     {'name': 'xs', 'value': '50%3ANQbSUEMGSilOuA%3A2%3A1686258626%3A-1%3A-1',
                      'domain': '.facebook.com', 'path': '/', 'expires': 1717794624.835686, 'httpOnly': True,
                      'secure': True, 'sameSite': 'None'}, {'name': 'fr',
                                                            'value': '0zof7rQDw6qA29DZN.AWWXOygMbI29HeM5-ZC7Rcdtg60.BkgkPA.HR.AAA.0.0.BkgkPA.AWVIdCnRLEM',
                                                            'domain': '.facebook.com', 'path': '/',
                                                            'expires': 1694034620.835712, 'httpOnly': True,
                                                            'secure': True, 'sameSite': 'None'},
                     {'name': 'm_page_voice', 'value': '100092379542437', 'domain': '.facebook.com', 'path': '/',
                      'expires': 1694034630.393375, 'httpOnly': True, 'secure': True, 'sameSite': 'None'}]:
            ydl.cookiejar.set_cookie(
                Cookie(name=auth['name'], value=auth['value'], domain=auth['domain'], expires=auth['expires'],
                       secure=auth['secure'], version=0, port=None, path='/', discard=False,
                       comment=None, comment_url=None, rest={'HttpOnly': None},
                       domain_initial_dot=True, port_specified=False, domain_specified=True, path_specified=False))
        ydl.download(['https://www.facebook.com/100057495277210/videos/1152078748829838'])
