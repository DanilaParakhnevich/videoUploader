from playwright.sync_api import sync_playwright
from time import sleep

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto('https://passport.yandex.ru/auth')
    page.type('input[name=login]', '')
    page.keyboard.press('Enter')
    sleep(1)
    page.type('input[name=passwd]', '')
    page.keyboard.press('Enter')
    sleep(1)
    page.click(selector='.Button2_type_submit')
    sleep(1)
    a = input()
    page.type('input[name=phoneCode]', a)
    sleep(1)
    page.screenshot(path="s1.jpg")