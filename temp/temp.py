from playwright.sync_api import sync_playwright
from time import sleep

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://passport.yandex.ru/auth')
    page.type('input[name=login]', 'beylon228822@gmail.com')
    page.keyboard.press('Enter')
    sleep(1)
    page.type('input[name=passwd]', 'Molotok5074344')
    page.keyboard.press('Enter')
    sleep(1)
    page.goto('https://dzen.ru/video')
    page.click(selector='.desktop-header2__profile-menu')
    sleep(1)
    page.screenshot(path="s1.jpg")