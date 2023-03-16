import os
import sqlite3

import Constants
import Variables
import telebot
from telebot import types
from telebot.types import ReplyKeyboardRemove

bot = telebot.TeleBot(Constants.token)


@bot.message_handler(regexp="\w+@\w+\.\w+")
def set_email(message):
    Variables.email = message.text
    bot.send_message(message.from_user.id, text="Email сохранен")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Начать")
    markup.add(button1)
    bot.send_message(message.from_user.id, text=Constants.invitation, reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, text=Constants.intro)
    if Variables.email is None:
        bot.send_message(message.from_user.id, "Введите Email")


@bot.message_handler(regexp='Начать')
def set_first(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton(Constants.Questions_and_answers[1])
    button2 = types.KeyboardButton(Constants.Questions_and_answers[2])
    markup.add(button1, button2)
    bot.send_message(message.from_user.id, Constants.Questions_and_answers[0], reply_markup=markup)
    Variables.current_counter = 1


@bot.message_handler(regexp='^[аб]\) ')
def process(message):
    if message.text.startswith('а'):
        if Variables.current_counter % 7 == 1:
            Variables.ie += 1
        elif Variables.current_counter % 7 in (2, 3):
            Variables.sn += 1
        elif Variables.current_counter % 7 in (4, 5):
            Variables.tf += 1
        else:
            Variables.jp += 1

    if Variables.current_counter == 69:
        result = ('E' if Variables.ie > 5 else 'I') + \
                 ('S' if Variables.sn > 10 else 'N') + \
                 ('T' if Variables.tf > 10 else 'F') + \
                 ('J' if Variables.jp > 10 else 'P')
        wrap_up(message, result)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton(Constants.Questions_and_answers[Variables.current_counter * 3 + 1])
    button2 = types.KeyboardButton(Constants.Questions_and_answers[Variables.current_counter * 3 + 2])
    markup.add(button1, button2)
    bot.send_message(message.from_user.id, Constants.Questions_and_answers[Variables.current_counter * 3],
                     reply_markup=markup)
    Variables.current_counter += 1

    # for debug, don't delete
    # print(Variables.ie, Variables.sn, Variables.tf, Variables.jp)


def wrap_up(message, result):
    bot.send_message(message.from_user.id,
                     f"Ваш результат: {result}; параметры: IE={Variables.ie}, SN={Variables.sn}, TF={Variables.tf}, JP={Variables.jp}")

    with open(os.path.join("results", result + ".md"), 'r', encoding='utf-8') as f:
        bot.send_document(message.from_user.id, f, reply_markup=ReplyKeyboardRemove())

    add_to_database(result)

    Variables.email = None
    Variables.current_counter = 0

    bot.send_message(message.from_user.id, "Кликните на /start, чтобы начать заново")

def add_to_database(result):
    try:
        sqlite_connection = sqlite3.connect('results.db')
        cursor = sqlite_connection.cursor()

        # create
        create_query = '''
        CREATE TABLE IF NOT EXISTS results (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             email TEXT,
             code TEXT NOT NULL,
             ie INTEGER NOT NULL,
             sn INTEGER NOT NULL,
             tf INTEGER NOT NULL,
             jp INTEGER NOT NULL);'''
        cursor.execute(create_query)
        sqlite_connection.commit()

        #insert
        insert_query = f"INSERT INTO results (email, code, ie, sn, tf, jp) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(insert_query, (Variables.email, result, Variables.ie, Variables.sn, Variables.tf, Variables.jp))
        sqlite_connection.commit()

        # debug via select all
        select_all_query = '''SELECT * FROM results'''
        cursor.execute(select_all_query)
        print(cursor.fetchall())
        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")



bot.polling(none_stop=True, interval=0)
