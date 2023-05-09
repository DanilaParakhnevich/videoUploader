from service.StateService import StateService
import json
import os

state_service = StateService()
locale_json = json.load(open(os.path.abspath(f'service/locale/{state_service.get_settings().language}.json')))

def get_str(key: str) -> str:
    return locale_json[key]

def add_new_locale(file_dir: str, new_file_name: str):
    os.rename(file_dir, os.path.abspath(f'service/locale/{new_file_name}'))

def get_all_locales() -> list:
    result = list()
    for locale in os.listdir(os.path.abspath('service/locale/')):
        result.append(locale.replace('.json', ''))
    return result
