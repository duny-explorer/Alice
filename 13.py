from flask import request
import logging
import json
import random
from DBManager import *


logging.basicConfig(level=logging.INFO)
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
        }
    }

    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = \
            'Привет! Я помогу тебе подготовиться к тестовой части ОГЭ по математике. Только сначала скажи свой имя.'
        sessionStorage[user_id] = {
            'first_name': None,
            'test': False,
            'theory': False,
            'task': False,
            'task_number': None,
            'task_theme': None,
            'test_number': None,
            'theory_theme': None
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = \
                f'Приятно познакомиться, {first_name.title()}.Здесь есть три раздела: теория (материалы или справка), задания по темам (задания) и пробник (тест). Чтобы вернуться в начало набо написать "меню". Если всё понятно, то тогда поехали!!!'
            res['response']['buttons'] = [
                {
                    'title': 'Теория',
                    'hide': True
                },
                {
                    'title': 'Задания',
                    'hide': True
                },
                {
                    'title': 'Тест',
                    'hide': True
                }
            ]
    else:
        if 'меню' in req['request']['nlu']['tokens']:
            first_name = sessionStorage[user_id]['first_name']
            sessionStorage[user_id] = {
                'test': False,
                'theory': False,
                'task': False,
                'task_number': None,
                'task_theme': None,
                'test_number': None,
                'theory_theme': None
            }
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = \
                f'{sessionStorage[user_id]["first_name"].title()}, смотри.Здесь есть три раздела: теория (материалы или справка), задания по темам (задания) и пробник (тест). Чтобы вернуться в начало набо написать "меню". Если всё понятно, то тогда поехали!!!'

        if sessionStorage[user_id]['task']:
            if sessionStorage[user_id]['task_number']:
                if 'да' in req['request']['nlu']['tokens']:
                    if len(sessionStorage[user_id]['task_number']) == \
                            len(Tasks.query.filter_by(task=sessionStorage[user_id]['task_theme'])):
                        res['response']['text'] = "I'm so sorry, но задания по данной теме закончились. Выбери другой раздел:"
                    else:
                        sessionStorage[user_id]['task_number'] += 1

                elif 'нет' in req['request']['nlu']['tokens']:
                    res['response']['text'] = 'Ну и ладно! С тебя наверное хватит. Выбери тогда другой раздел:'
                    res['end_session'] = True
            else:
                res['response']['text'] = \
                    f'Здесь, { sessionStorage[user_id]["first_name"].title() }, у нас с тобой задачи по темам. Кого хочешь выбирай:'
        if sessionStorage[user_id]['test']:
            if sessionStorage[user_id]['test_number']:
                pass


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
