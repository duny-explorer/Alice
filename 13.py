from flask import Flask, request
import logging
import json
import random
from flask_sqlalchemy import SQLAlchemy
import re


'''
Ничего такого, просто небольшой заачник по геометрии ))
P.S Просто строчка чтобы строк набрать
'''


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
    help = db.Column(db.String(100), unique=False, nullable=False)


db.create_all()

logging.basicConfig(level=logging.INFO)
part_tasks = '1) Окружность 2) Многоугольники 3) Площади фигур 4) Практические задачки'
sessionStorage = {}
theory = {1: ('Свойства равнобедренного треугольника', '1. Углы при основании равны. 2. Высота (медиана, биссектриса) '
                                                       'проведённая является ещё медианой и биссектриссой (высотой) '
                                                       '3. Высоты (медианы, биссектрисы) проведённые к юоковым '
                                                       'сторонам равны'),
          2: ('Свойства равностороннего треугольника', '1. Все углы равны и по 60 градусов. 2. Цент вписанной и '
                                                       'описанной окружности совпадают. 3. Любая высота (медиана, '
                                                       'биссектриса) является медианой и биссектрисой (высотой)'),
          3: ('Площади фигур', '1540737/fb8d2cd67e975fbe92ca'),
          4: ('Признаки подобия треугольков', '1. По двум углам. 2. По двум порпорциональным сторонам и углу между '
                                              'ними. 3. По трём порпорциональным сторонам')}


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
    """
    Эта та часть кода, которую лучше не коментить, т.к это один большой костыль
    """
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = \
            'Привет! Здесь собраны различные задачи по геометрии из тестовой части экзамена ОГЭ по математике, ' \
            'чисто чтобы размять мозги. Только сначала скажи своё имя. А то ты меня знаешь, а я тебя нет. '
        sessionStorage[user_id] = {
            'first_name': None,
            'test': False,
            'theory': False,
            'task': False,
            'number': None,
            'item': None,
            'wga': '',
            'task_theme': None,
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
                f'Приятно познакомиться, {first_name.title()}.Здесь есть три раздела: теория (материалы или справка),' \
                f'задания по темам (задания) и пробник (тест). Чтобы вернуться в начало набо написать "меню" (а ' \
                f'так везде кроме выбора раздела пишем цифры). Если всё понятно, то тогда поехали!!! '
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
        if req['request']['original_utterance'].lower() in \
                ['помощь знатоков', 'помощь зала', 'звонок другу', 'красавчик, помоги', 'помощь'] and \
                sessionStorage[user_id]['item']:
            res['response']['text'] = sessionStorage[user_id]['item'].help

        elif 'меню' in req['request']['nlu']['tokens']:
            first_name = sessionStorage[user_id]['first_name']
            sessionStorage[user_id] = {
                'test': False,
                'theory': False,
                'task': False,
                'number': None,
                'task_theme': None,
                'wga': '',
                'item': None,
            }
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = \
                f'{sessionStorage[user_id]["first_name"].title()}, смотри. Здесь есть три раздела: теория (материалы ' \
                f'или справка), задания по темам (задания) и пробник (тест). Чтобы вернуться в начало набо ' \
                f'написать "меню". Если всё понятно, то тогда поехали!!! '
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

        elif not sessionStorage[user_id]['task'] and not sessionStorage[user_id]['test'] \
                and not sessionStorage[user_id]['theory']:
            if req['request']['original_utterance'].lower() in ['задания', 'задания по темам']:
                sessionStorage[user_id]['task'] = True
                res['response']['text'] = \
                    f'Здесь, {sessionStorage[user_id]["first_name"].title()}, у нас с тобой задачи по темам. Кого ' \
                    f'хочешь выбирай: ' + part_tasks
            elif req['request']['original_utterance'].lower() in ['материалы', 'справка', 'теория']:
                sessionStorage[user_id]['theory'] = True
                res['response']['text'] = '1) Свойста равнобедреных треугольников 2) Свойства равностороних ' \
                                          'треугольников 3) Площади фигур 4) Признаки подобия треугольников '
            elif req['request']['original_utterance'].lower() in ['тест', 'пробник']:
                sessionStorage[user_id]['test'] = True
                sessionStorage[user_id]['number'] = 1
                sessionStorage[user_id]['item'] = \
                    random.choice(Tasks.query.filter_by(task=sessionStorage[user_id]['number']).all())
                task = sessionStorage[user_id]['item']
                res['response']['text'] = '4 вопроса. Дерзай. ' + task.text
                res['response']['tts'] = '<speaker audio="alice-music-horn-1.opus">'

                if task.image:
                    res['response']['card'] = {}
                    res['response']['card']['type'] = 'BigImage'
                    res['response']['card']['title'] = res['response']['text']
                    res['response']['card']['image_id'] = task.image
            else:
                res['response']['text'] = 'Такого раздела у меня нет...'

        elif sessionStorage[user_id]['task']:
            if sessionStorage[user_id]['task_theme']:
                if not sessionStorage[user_id]['item']:
                    if 'да' in req['request']['nlu']['tokens']:
                        if sessionStorage[user_id]['number'] == \
                                len(Tasks.query.filter_by(task=sessionStorage[user_id]['task_theme']).all()):
                            res['response']['text'] = \
                                "I'm so sorry, но задания по данной теме закончились. Выбери другой раздел: " + \
                                part_tasks
                            sessionStorage[user_id]['number'] = None
                            sessionStorage[user_id]['task_theme'] = None
                        else:
                            sessionStorage[user_id]['number'] += 1
                            task = \
                                Tasks.query.filter_by(task=sessionStorage[user_id]['task_theme']).all()[
                                    sessionStorage[user_id]['number'] - 1]
                            sessionStorage[user_id]['item'] = task
                            res['response']['text'] = task.text
                            if task.image:
                                res['response']['card'] = {}
                                res['response']['card']['title'] = task.text
                                res['response']['card']['type'] = 'BigImage'
                                res['response']['card']['image_id'] = task.image

                            res['response']['buttons'] = [
                                {
                                    'title': random.choice(['Помощь знатоков',
                                                            'Помощь зала', 'Звонок другу',
                                                            'Красавчик, помоги', 'Помощь']),
                                    'hide': True
                                }
                            ]

                    elif 'нет' in req['request']['nlu']['tokens']:
                        res['response']['text'] = 'Ну и ладно! С тебя наверное хватит. Выбери тогда другой раздел:' + \
                                                  part_tasks
                        sessionStorage[user_id]['number'] = None
                        sessionStorage[user_id]['task_theme'] = None
                    else:
                        res['response']['text'] = 'Так продолжим или нет?'

                    return
                else:
                    if str(sessionStorage[user_id]['item'].tr) == req['request']['original_utterance'].lower().replace(
                            ',', '.'):
                        res['response']['text'] = random.choice(['Молодец!', 'Правильно.', 'Верно.']) + ' Продолжим?'
                        res['response']['tts'] = '<speaker audio="alice-sounds-game-win-1.opus">'
                    else:
                        if sessionStorage[user_id]['item'].image_solution:
                            res['response']['card'] = {}
                            res['response']['card']['type'] = 'BigImage'
                            res['response']['card']['image_id'] = sessionStorage[user_id]['item'].image_solution
                            res['response']['card']['title'] =\
                                random.choice(['Эх ты...', 'Неправильно.', 'Не верно.']) + ' Вот решение: ' + \
                                sessionStorage[user_id]['item'].solution + ' Продолжаем?'

                        res['response']['tts'] = '<speaker audio="alice-sounds-game-loss-3.opus">'
                        res['response']['text'] = \
                            random.choice(['Эх ты...', 'Неправильно.', 'Не верно.']) + \
                            ' Вот решение: ' + sessionStorage[user_id]['item'].solution + ' Продолжаем?'

                    sessionStorage[user_id]['item'] = None

                    return
            else:
                if req['request']['original_utterance'].isdigit() and int(
                        req['request']['original_utterance']) in range(1, 5):
                    sessionStorage[user_id]['number'] = 1
                    sessionStorage[user_id]['task_theme'] = int(req['request']['original_utterance'])
                    task = Tasks.query.filter_by(task=sessionStorage[user_id]['task_theme']).all()[
                        sessionStorage[user_id]['number'] - 1]
                    sessionStorage[user_id]['item'] = task
                    res['response']['text'] = task.text
                    res['response']['buttons'] = [
                        {
                            'title': random.choice(
                                ['Помощь знатоков', 'Помощь зала', 'Звонок другу', 'Красавчик, помоги', 'Помощь']),
                            'hide': True
                        }
                    ]
                    if task.image:
                        res['response']['card'] = {}
                        res['response']['card']['type'] = 'BigImage'
                        res['response']['card']['title'] = task.text
                        res['response']['card']['image_id'] = task.image

                    res['response']['tts'] = '<speaker audio="alice-music-horn-1.opus">'
                else:
                    res['response']['text'] = 'Такой темы нет. Напиши ещё раз.'

                return

        elif sessionStorage[user_id]['theory']:
            if int(req['request']['original_utterance']) in range(1, 5):
                if len(theory[int(req['request']['original_utterance'])][1]) > 40:
                    res['response']['text'] = theory[int(req['request']['original_utterance'])][1]
                else:
                    res['response']['text'] = theory[int(req['request']['original_utterance'])][0]
                    res['response']['card'] = {}
                    res['response']['card']['type'] = 'BigImage'
                    res['response']['card']['image_id'] = theory[int(req['request']['original_utterance'])][1]
            else:
                res['response']['text'] = 'Такого раздела в теории нет'

        elif sessionStorage[user_id]['test']:
            if str(sessionStorage[user_id]['item'].tr) == req['request']['original_utterance'].lower().replace(',',
                                                                                                               '.'):
                sessionStorage[user_id]['wga'] += '1'
            else:
                sessionStorage[user_id]['wga'] += '0'

            if sessionStorage[user_id]['number'] == 4:
                if sessionStorage[user_id]['wga'].count('0') == 0:
                    res['response']['text'] = 'Молодец, всё правильно!!! Не хочешь ли проверить ещё раз?'

                else:
                    res['response']['text'] = 'Не всё идеально. Есть ошибки в {} задании. Повторим?'.format(
                        ','.join([str(i.start() + 1) for i in re.finditer('0', sessionStorage[user_id]['wga'])]))

                sessionStorage[user_id]['number'] = None
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    }
                ]

                return

            elif not sessionStorage[user_id]['number'] and sessionStorage[user_id]['wga']:
                if 'да' in req['request']['nlu']['tokens']:
                    sessionStorage[user_id]['wga'] = ''
                    sessionStorage[user_id]['number'] = 1
                    sessionStorage[user_id]['item'] = random.choice(
                        Tasks.query.filter_by(task=sessionStorage[user_id]['number']).all())
                    task = sessionStorage[user_id]['item']
                    res['response']['text'] = '4 вопроса. Дерзай. ' + task.text

                    if task.image:
                        res['response']['card'] = {}
                        res['response']['card']['type'] = 'BigImage'
                        res['response']['card']['title'] = task.text
                        res['response']['card']['image_id'] = task.image
                elif 'нет' in req['request']['nlu']['tokens']:
                    first_name = sessionStorage[user_id]['first_name']
                    sessionStorage[user_id] = {
                        'test': False,
                        'theory': False,
                        'task': False,
                        'number': None,
                        'task_theme': None,
                        'wga': '',
                        'item': None,
                    }
                    sessionStorage[user_id]['first_name'] = first_name
                    res['response']['text'] = \
                        f'{sessionStorage[user_id]["first_name"].title()}, смотри. Здесь есть три раздела: теория (' \
                        f'материалы или справка), задания по темам (задания) и пробник (тест). Чтобы вернуться в ' \
                        f'начало набо написать "меню". Если всё понятно, то тогда поехали!!! '
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
                    res['response'][
                        'text'] = 'Давай, с чувством, с толком, с растоновкой. Будешь ещё раз проходить тест?'

                return

            sessionStorage[user_id]['number'] += 1
            task = random.choice(Tasks.query.filter_by(task=sessionStorage[user_id]['number']).all())
            sessionStorage[user_id]['item'] = task

            if task.image:
                res['response']['text'] = 'Задача'
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = task.text
                res['response']['card']['image_id'] = task.image
            else:
                res['response']['text'] = task.text

            return

        return


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
