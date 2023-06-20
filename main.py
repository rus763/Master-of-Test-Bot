# Author:   Ruslan G. Sobolev
# Support:  r.g.sobolev@ya.ru
# Project:  Master of test - telegram bot
#
# Main script of telegram bot

import telebot
import json

from telebot import types

TOKEN = '6213894744:AAHGezbcf5juvm06n81sJGlutPJw51slUz4'

bot = telebot.TeleBot(TOKEN)

# Обработка команд '/start' и '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Привет, меня зовут Квиз-Бот.
В этом чате ты можешь пройти тест. Для этого введи команду /quiz.\
""")

def status_w(chat_id):
    # функция, которая увеличивает кол-во баллов на 1 при правильном ответе 
    chat_id = str(chat_id)
    # Открываем БД для чтения
    with open('db\client.json') as json_file:
        data = json.load(json_file)
    # Проверяем существует ли пользователь в БД
    if not (chat_id in data):
    #     data[chat_id]['status'] += 1
    #     data[chat_id]['name'] = "Руслан"
    # else:
        new_chat = {chat_id: {'status': 1, 'points': 0}}
        data.update(new_chat)
    file = open('db\client.json', 'w')
    file.write(json.dumps(data))
    file.close()

def status_restart(chat_id):
    # функция для обнуления значений
    chat_id = str(chat_id)
    # Открываем БД для чтения
    with open('db\client.json') as json_file:
        data = json.load(json_file)
    # Проверяем если такой пользователь в БД
    if (chat_id in data):
        data[chat_id]['status'] = 1
        data[chat_id]['points'] = 0
    else:
        new_chat = {chat_id: {'status': 1, 'points': 0}}
        data.update(new_chat)
    file = open('db\client.json', 'w')
    file.write(json.dumps(data))
    file.close()


def point_summ(chat_id, point):
    # функция для подсчета баллов
    chat_id = str(chat_id)
    # Открываем БД для чтения
    with open('db\client.json') as json_file:
        data = json.load(json_file)
    # Проверяем если такой пользователь в БД
    if (chat_id in data):
        data[chat_id]['points'] += point
        data[chat_id]['status'] += 1
    else:
        new_chat = {chat_id: {'status': 1, 'points': 0}}
        data.update(new_chat)
    file = open('db\client.json', 'w')
    file.write(json.dumps(data))
    file.close()


def status_r(chat_id):
    # функция возвращает номер текущего вопроса
    chat_id = str(chat_id)
    # Узнаем номер вопроса
    with open('db\client.json') as json_file:
        data = json.load(json_file)
    return data[chat_id]['status']

def get_answers(markup, status1):
    # функция возвращает клавиатуру с ответами
    status1 = str(status1)
    with open('questions.json') as json_file:
        data = json.load(json_file)
    for key, result in data[status1]['answers'].items():
        markup.row(types.InlineKeyboardButton(key, callback_data=result))
    # status = status + 1
    return markup

def get_question(status1):
     # функция возвращает текст вопроса
     status1 = str(status1)
     with open('questions.json') as json_file:
        data = json.load(json_file)
     return data[status1]['question']

def get_len_question():
     # функция возвращает кол-во вопросов
     with open('questions.json') as json_file:
        data = json.load(json_file)
     return len(data)

def get_points(chat_id):
     # функция возвращает текущий счет
     chat_id = str(chat_id)
     with open('questions.json') as json_file:
        questions = json.load(json_file)
     with open('db\client.json') as json_file:
        client = json.load(json_file)
     return str(client[chat_id]['points']) + "/" + str(len(questions))

# обработчик команды /quiz
@bot.message_handler(commands=['quiz'])
def send_quiz(message):
    # bot.reply_to(message, "{0.first_name}, Добро пожаловать в квиз-Бот <b>{1.first_name}</b>!\n".format(message.from_user, bot.get_me()), parse_mode='html')
    bot.send_message(message.chat.id, "{0.first_name}, Добро пожаловать в Бот <b>{1.first_name}</b>!\n".format(message.from_user, bot.get_me()), parse_mode='html')
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    status_w(message.chat.id)
    status = status_r(message.chat.id)
    question_count = get_len_question()
    if status > question_count:
        #Начать сначала
        markup = markup.row(types.InlineKeyboardButton('Еще раз', callback_data='restart'))
        quest = 'Начать с начала'
    elif status > 2:
        # Продолжить
        markup = markup.row(types.InlineKeyboardButton('Продолжить', callback_data='continue'))
        quest = 'Продолжить'
    else:
        # Начать 
        markup = markup.row(types.InlineKeyboardButton('Начать тест', callback_data='start'))
        quest = 'Тест на знание фильма <b>«Любовь и голуби»</b>: \nна все 14 вопросов ответит только тот, кто смотрел больше 10 раз. \nДля прохождения теста нажмите на кнопку \"Начать тест\"👇'
        # markup = get_answers(markup, status)
        # quest = get_question(status)
    bot.send_message(message.chat.id, quest, parse_mode='html', reply_markup=markup)

# answer
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            markup = types.InlineKeyboardMarkup(row_width=1)
            status_end = get_len_question()
            if call.data == 'correct':
                status = status_r(call.message.chat.id)
                point_summ(call.message.chat.id, 1)
                points = get_points(call.message.chat.id)
                ans1 = 'Правильный ответ!😎\n\nВаш счет ' + points
                if status == status_end:
                    markup.row(types.InlineKeyboardButton('Завершить тест!', callback_data='next'))
                else:
                    markup.row(types.InlineKeyboardButton('Следующий вопрос', callback_data='next'))
            elif call.data == 'wrong':
                status = status_r(call.message.chat.id)
                point_summ(call.message.chat.id, 0)
                points = get_points(call.message.chat.id)
                ans1 = 'Увы, ответ не правильный😔\n\nВаш счет ' + points
                if status == status_end:
                    markup.row(types.InlineKeyboardButton('Завершить тест!', callback_data='next'))
                else:
                    markup.row(types.InlineKeyboardButton('Следующий вопрос', callback_data='next'))
            elif call.data == 'start':
                status = status_r(call.message.chat.id)
                ans1 = get_question(status)
                markup = get_answers(markup, status)
                # status_w(call.message.chat.id)
            elif call.data == 'restart':
                status_restart(call.message.chat.id)
                status = status_r(call.message.chat.id)
                ans1 = get_question(status)
                markup = get_answers(markup, status)
                status_w(call.message.chat.id)
            elif call.data == 'continue':
                # status_restart(call.message.chat.id)
                status = status_r(call.message.chat.id)
                ans1 = get_question(status)
                markup = get_answers(markup, status)
                status_w(call.message.chat.id)
            elif call.data == 'next':
                status = status_r(call.message.chat.id)
                if status > get_len_question():
                    points = get_points(call.message.chat.id)
                    ans1 = 'Тест пройден\n\nВаш счет ' + points
                    markup = markup.row(types.InlineKeyboardButton('Еще раз', callback_data='restart'))
                else:
                    ans1 = get_question(status)
                    markup = get_answers(markup, status)
                    status_w(call.message.chat.id)
            # remove inline
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=ans1, reply_markup=markup)

    except Exception as e:
        print(repr(e))

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)

bot.infinity_polling()