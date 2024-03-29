from service.StateService import StateService
import json
import os

# Мною был выбран подход реализовать свою локализацию через .json, тк необходимо было динамическое добавление локализаций
state_service = StateService()
locale_json = json.load(open(os.path.abspath(f'service/locale/{state_service.get_settings().language}.json'), encoding='utf8'))

def get_str(key: str) -> str:
    try:
        return locale_json[key]
    except:
        return key

def add_new_locale(file_dir: str):
    new_locale_json = json.load(open(file_dir))
    if len(new_locale_json) != len(locale_json):
        raise Exception

    for locale_item in locale_json:
        if new_locale_json[locale_item] is None:
            raise Exception

    os.rename(file_dir, os.path.abspath(f'service/locale/{os.path.basename(file_dir)}'))

def get_all_locales() -> list:
    result = list()
    for locale in os.listdir(os.path.abspath('service/locale/')):
        result.append(locale.replace('.json', ''))
    return result
