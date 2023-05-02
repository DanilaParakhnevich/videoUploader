from playwright.sync_api import sync_playwright
from time import sleep

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()

    context.add_cookies([{'name': 'yandex_login', 'value': 'dendillllll', 'domain': '.yandex.ru', 'path': '/', 'expires': 1711084889.156457, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'uniqueuid', 'value': '516135181679548875', 'domain': 'passport.yandex.ru', 'path': '/', 'expires': 1714108875.338208, 'httpOnly': True, 'secure': True, 'sameSite': 'Lax'}, {'name': 'gdpr', 'value': '0', 'domain': '.yandex.ru', 'path': '/', 'expires': 1711084875, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': '_ym_uid', 'value': '1679548876709931997', 'domain': '.yandex.ru', 'path': '/', 'expires': 1711084875, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': '_ym_d', 'value': '1679548876', 'domain': '.yandex.ru', 'path': '/', 'expires': 1711084875, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'yabs-sid', 'value': '2025944891679548875', 'domain': 'mc.yandex.ru', 'path': '/', 'expires': -1, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'i', 'value': 'Bq3phtVpcl6RImabFYtPdh4DqOjaRAEKe9CPVvWjFmmqzkRzA+uO2jl6MNsO9IFVGpHTeoKbOAteru+g8Z5RT0GgB+E=', 'domain': '.yandex.ru', 'path': '/', 'expires': 1714108875.918943, 'httpOnly': True, 'secure': True, 'sameSite': 'None'}, {'name': 'yandexuid', 'value': '4751752361679548875', 'domain': '.yandex.ru', 'path': '/', 'expires': 1714108875.918962, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'yuidss', 'value': '4751752361679548875', 'domain': '.yandex.ru', 'path': '/', 'expires': 1714108875.918971, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'ymex', 'value': '1994908875.yrts.1679548875#1994908875.yrtsi.1679548875', 'domain': '.yandex.ru', 'path': '/', 'expires': 1711084875.918979, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': '_ym_isad', 'value': '2', 'domain': '.yandex.ru', 'path': '/', 'expires': 1679620875, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': '_ym_visorc', 'value': 'b', 'domain': '.yandex.ru', 'path': '/', 'expires': 1679550676, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'Session_id', 'value': '3:1679548889.5.0.1679548889096:_vA1Lg:56.1.2:1|989036743.0.2.3:1679548889|3:10267333.752473.oxZili-zwktsZ12WIsE_gU3H8H0', 'domain': '.yandex.ru', 'path': '/', 'expires': 1714108889.156198, 'httpOnly': True, 'secure': True, 'sameSite': 'None'}, {'name': 'sessionid2', 'value': '3:1679548889.5.0.1679548889096:_vA1Lg:56.1.2:1|989036743.0.2.3:1679548889|3:10267333.752473.fakesign0000000000000000000', 'domain': '.yandex.ru', 'path': '/', 'expires': 1714108889.156293, 'httpOnly': True, 'secure': True, 'sameSite': 'None'}, {'name': 'sessguard', 'value': '1.1679548889.1679548889096:_vA1Lg:56..3.500:33373.vzmdjbrd.77THVzzf2OiEEGajxZP8WEqcvKE', 'domain': '.passport.yandex.ru', 'path': '/', 'expires': 1714108889.156325, 'httpOnly': True, 'secure': True, 'sameSite': 'None'}, {'name': 'yp', 'value': '1994908889.udn.cDpkZW5kaWxsbGxsbA%3D%3D', 'domain': '.yandex.ru', 'path': '/', 'expires': 1714108889.156354, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'L', 'value': 'Y2pBewoMUnl6RA9ZXHgIbgJqBnUIY1N8Pi00Kig2ND8jHSs=.1679548889.15290.370267.cbd399515790a98d35b2ed45de2fe542', 'domain': '.yandex.ru', 'path': '/', 'expires': 1714108889.156401, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'lah', 'value': '2:1742620889.10021495.z8S65UY_fsu3U2fP.3jQuA0AjzXEedZYMHej7yb-Wu7bqQMWmYH1rqoNfOL-SWPlmwHKF46KYl3dCwI0-AOeTzKamqfo.v6PxiKL2AJKiMcVKud3Pbg', 'domain': '.passport.yandex.ru', 'path': '/', 'expires': 1714108889.156497, 'httpOnly': True, 'secure': True, 'sameSite': 'None'}, {'name': 'mda2_beacon', 'value': '1679548889123', 'domain': '.passport.yandex.ru', 'path': '/', 'expires': 1714108889.156538, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'pf', 'value': 'eyJmbGFzaCI6e319', 'domain': 'passport.yandex.ru', 'path': '/', 'expires': -1, 'httpOnly': True, 'secure': False, 'sameSite': 'Lax'}, {'name': 'pf.sig', 'value': 'WEkihpon3qfXt708UtZSzfT2k62TloAdz1jg6_iLs5Q', 'domain': 'passport.yandex.ru', 'path': '/', 'expires': -1, 'httpOnly': True, 'secure': False, 'sameSite': 'Lax'}, {'name': 'ys', 'value': 'udn.cDpkZW5kaWxsbGxsbA%3D%3D#c_chck.3343768409', 'domain': '.yandex.ru', 'path': '/', 'expires': -1, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'mda2_domains', 'value': 'ya.ru', 'domain': '.passport.yandex.ru', 'path': '/', 'expires': 1714108889.412273, 'httpOnly': False, 'secure': True, 'sameSite': 'Lax'}, {'name': 'Session_id', 'value': '3:1679548889.5.0.1679548889096:_vA1Lg:56.1.2:1|989036743.0.2.3:1679548889|6:10180713.219786.nNPknVoQ3PQhpzL8mZmQHh5VXI0', 'domain': '.ya.ru', 'path': '/', 'expires': 1714108889.561331, 'httpOnly': True, 'secure': True, 'sameSite': 'None'}, {'name': 'yandex_login', 'value': 'dendillllll', 'domain': '.ya.ru', 'path': '/', 'expires': 1711084889.561434, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'yp', 'value': '1994908889.udn.cDpkZW5kaWxsbGxsbA%3D%3D', 'domain': '.ya.ru', 'path': '/', 'expires': 1714108889.561462, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'ys', 'value': 'udn.cDpkZW5kaWxsbGxsbA%3D%3D#c_chck.3343768409', 'domain': '.ya.ru', 'path': '/', 'expires': -1, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'i', 'value': 'Bq3phtVpcl6RImabFYtPdh4DqOjaRAEKe9CPVvWjFmmqzkRzA+uO2jl6MNsO9IFVGpHTeoKbOAteru+g8Z5RT0GgB+E=', 'domain': '.ya.ru', 'path': '/', 'expires': 1714108889.56151, 'httpOnly': True, 'secure': True, 'sameSite': 'None'}, {'name': 'yandexuid', 'value': '4751752361679548875', 'domain': '.ya.ru', 'path': '/', 'expires': 1714108889.561537, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'L', 'value': 'Y2pBewoMUnl6RA9ZXHgIbgJqBnUIY1N8Pi00Kig2ND8jHSs=.1679548889.15290.370267.cbd399515790a98d35b2ed45de2fe542', 'domain': '.ya.ru', 'path': '/', 'expires': 1714108889.56156, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}, {'name': 'mda2_beacon', 'value': '1679548889385', 'domain': '.ya.ru', 'path': '/', 'expires': 1714108889.561585, 'httpOnly': False, 'secure': True, 'sameSite': 'None'}, {'name': 'sso_status', 'value': 'sso.passport.yandex.ru:synchronized', 'domain': '.ya.ru', 'path': '/', 'expires': 1679559689, 'httpOnly': False, 'secure': False, 'sameSite': 'Lax'}])

    page = context.new_page()
    page.goto('https://dzen.ru/video')
    # page.goto('https://passport.yandex.ru/auth')
    # page.type('input[name=login]', 'beylon228822@gmail.com')
    # page.keyboard.press('Enter')
    # sleep(1)
    # page.type('input[name=passwd]', 'Molotok.5074344')
    # page.keyboard.press('Enter')
    # sleep(1)
    # page.click(selector='.Button2_type_submit')
    # sleep(1)
    # a = input()
    # page.screenshot(path="s1.jpg")
    # page.type('input[name=phoneCode]', a)
    sleep(1)
    page.screenshot(path="s1.jpg")
    # print(page.context.cookies())
