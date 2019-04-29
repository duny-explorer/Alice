from flask import Flask, request
import logging
import json
import random
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.Integer, unique=False, nullable=False)
    text = db.Column(db.String(100), unique=False, nullable=False)
    image = db.Column(db.String(30), unique=True, nullable=True)
    tr = db.Column(db.Float, unique=False, nullable=False)
    solution = db.Column(db.String(100), unique=False, nullable=False)
    image_solution = db.Column(db.String(30), unique=True, nullable=True)

db.create_all()

logging.basicConfig(level=logging.INFO)
part_tasks = '7) Простые текстовые задачи'
sessionStorage = {}
sessionStorage2 = {}
images = {1: ('Формулы сокращённого умножения', '213044/029a455579c2370ebf33'), 2: ('Площади фигур', '1652229/36805165c74d9bae7606')}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
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
            'task_item': None,
            'task_theme': None,
            'test_number': None,
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
            return
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
                'task_item': None,
                'test_number': None,
            }
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = \
                f'{sessionStorage[user_id]["first_name"].title()}, смотри.Здесь есть три раздела: теория (материалы или справка), задания по темам (задания) и пробник (тест). Чтобы вернуться в начало набо написать "меню". Если всё понятно, то тогда поехали!!!'
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
            return

        if not sessionStorage[user_id]['task'] and not sessionStorage[user_id]['test'] and not sessionStorage[user_id]['theory']:
            if req['request']['original_utterance'].lower() in ['задания', 'задания по темам']:
                sessionStorage[user_id]['task'] = True
                res['response']['text'] = \
                    f'Здесь, { sessionStorage[user_id]["first_name"].title() }, у нас с тобой задачи по темам. Кого хочешь выбирай: ' + part_tasks
            elif req['request']['original_utterance'].lower() in ['материалы', 'справка', 'теория']:
                sessionStorage[user_id]['theory'] = True
                res['response']['text'] = '1) Формулы сокращённого умножения  2) Площади фигур'
            elif req['request']['original_utterance'].lower() in ['тест', 'пробник']:
                sessionStorage[user_id]['test'] = True
            else:
                res['response']['text'] = 'Такого раздела у меня нет...'

            return

        if sessionStorage[user_id]['task']:
            if sessionStorage[user_id]['task_theme']:
                if not sessionStorage[user_id]['task_item']:
                    if 'да' in req['request']['nlu']['tokens']:
                        if sessionStorage[user_id]['task_number'] == \
                                len(Tasks.query.filter_by(task=sessionStorage[user_id]['task_theme']).all()):
                            res['response']['text'] = "I'm so sorry, но задания по данной теме закончились. Выбери другой раздел: " + part_tasks
                            sessionStorage[user_id]['task_number'] = None
                            sessionStorage[user_id]['task_theme'] = None
                        else:
                            sessionStorage[user_id]['task_number'] += 1
                            task =  Tasks.query.filter_by(task=sessionStorage[user_id]['task_theme']).all()[sessionStorage[user_id]['task_number'] - 1]
                            sessionStorage[user_id]['task_item'] = task
                            res['response']['text'] = task.text
                            if task.image:
                                res['response']['card'] = {}
                                res['response']['card']['type'] = 'BigImage'
                                res['response']['card']['image_id'] = task.image

                    elif 'нет' in req['request']['nlu']['tokens']:
                        res['response']['text'] = 'Ну и ладно! С тебя наверное хватит. Выбери тогда другой раздел:\n' + part_tasks
                        sessionStorage[user_id]['task_number'] = None
                        sessionStorage[user_id]['task_theme'] = None
                    else:
                        res['response']['text'] = 'Так продолжим или нет?'

                    return
                else:
                    if sessionStorage[user_id]['task_item'].tr == float(req['request']['original_utterance'].lower().replace(',', '.')):
                        res['response']['text'] = random.choice(['Молодец!', 'Правильно.', 'Верно.']) + ' Продолжим?'
                    else:
                        res['response']['text'] = random.choice(['Эх ты...', 'Неправильно.', 'Не верно.']) + ' Вот решение: ' + sessionStorage[user_id]['task_item'].solution + ' Продолжаем?'

                        if sessionStorage[user_id]['task_item'].image_solution:
                            res['response']['card'] = {}
                            res['response']['card']['type'] = 'BigImage'
                            res['response']['card']['image_id'] = sessionStorage[user_id]['task_item'].image_solution

                    sessionStorage[user_id]['task_item'] = None
                    return
            else:
                if req['request']['original_utterance'].isdigit() and int(req['request']['original_utterance']) in [7, 18]:
                    sessionStorage[user_id]['task_number'] = 1
                    sessionStorage[user_id]['task_theme'] = int(req['request']['original_utterance'])
                    task =  Tasks.query.filter_by(task=sessionStorage[user_id]['task_theme']).all()[sessionStorage[user_id]['task_number'] - 1]
                    sessionStorage[user_id]['task_item'] = task
                    res['response']['text'] = task.text
                    if task.image:
                        res['response']['card'] = {}
                        res['response']['card']['type'] = 'BigImage'
                        res['response']['card']['image_id'] = task.image
                else:
                    res['response']['text'] = 'Такой темы нет. Напиши ещё раз.'

                return

        if sessionStorage[user_id]['theory']:
            if int(req['request']['original_utterance']) in [1, 2]:
                res['response']['text'] = images[int(req['request']['original_utterance'])][0]
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['image_id'] = images[int(req['request']['original_utterance'])][1]
            else:
                res['response']['text'] = 'Такого раздела в теории нет'

        return


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
