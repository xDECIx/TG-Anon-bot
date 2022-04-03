import config
import telebot

from telebot import types
from database import Database

db = Database("db.db")
bot = telebot.TeleBot(config.TOKEN, threaded=False)


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("🔎Поиск собеседника")
    markup.add(item1)
    return markup


def stop_dialog():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("☑️Сказать свой профиль")
    item2 = types.KeyboardButton("/stop")
    markup.add(item1, item2)


def stop_search():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('❌Остановить поиск')
    markup.add(item1)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("🔎Поиск собеседника")
    markup.add(item1)

    bot.send_message(message.chat.id, "Меню", reply_markup=markup)


@bot.message_handler(commands=['menu'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("🔎Поиск собеседника")
    markup.add(item1)

    bot.send_message(message.chat.id,
                     "Привет, {0.first_name}! Добро пожаловать в Анонимный чат! Нажми на поиск.".format(
                         message.from_user), reply_markup=markup)


@bot.message_handler(commands=['stop'])
def stop(message):
    chat_info = db.get_active_chat(message.chat.id)
    if chat_info != False:
        db.delete_chat(chat_info[0])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("🔜Следующий диалог")
        item2 = types.KeyboardButton("/menu")
        markup.add(item1, item2)

        bot.send_message(chat_info[1], "❗Собеседник покинул чат", reply_markup=markup)
        bot.send_message(message.chat.id, "❗Вы вышли из чата", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, '❗Вы не начали диалог')


@bot.message_handler(content_types=['text'])
def bot_message(message):
    if message.chat.type == 'private':
        if message.text == '🔎Поиск собеседника' or message.text == "🔜Следующий диалог":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton('❌Остановить поиск')
            markup.add(item1)

            chat_two = db.get_chat()  # id собеседника который в очереди 1ый

            if db.create_chat(message.chat.id, chat_two) == False:
                db.add_queue(message.chat.id)
                bot.send_message(message.chat.id, '⏳Поиск собеседника...', reply_markup=markup)
            else:
                mess = "✅Собеседник найден! Чтобы остановить диалог, нажми /stop"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = types.KeyboardButton("☑️Сказать свой профиль")
                item2 = types.KeyboardButton("/stop")
                markup.add(item1, item2)

                bot.send_message(message.chat.id, mess, reply_markup=markup)
                bot.send_message(chat_two, mess, reply_markup=markup)

        elif message.text == 'Stat':
            bot.send_message(message.chat.id, "<3")

        elif message.text == '❌Остановить поиск':
            db.delete_queue(message.chat.id)
            bot.send_message(message.chat.id, '❗Поиск остановлен, напишите /menu')

        elif message.text == "☑️Сказать свой профиль":
            chat_info = db.get_active_chat(message.chat.id)
            if chat_info != False:
                if message.from_user.username:
                    bot.send_message(chat_info[1], '@' + message.from_user.username)
                    bot.send_message(message.chat.id, "❗Вы сказали свой профиль")
                else:
                    bot.send_message(message.chat.id, '❗В вашем аккаунте не указан username')
            else:
                bot.send_message(message.chat.id, '❗Вы не начали диалог')

        else:
            if db.get_active_chat(message.chat.id) != False:
                chat_info = db.get_active_chat(message.chat.id)
                bot.send_message(chat_info[1], message.text)
            else:
                bot.send_message(message.chat.id, '❗Вы не начали диалог')


@bot.message_handler(content_types=['voice', 'video_note', 'sticker', 'audio', 'dice', 'photo', 'video', 'animation'])
def hi(message):
    chat_info = db.get_active_chat(message.chat.id)
    bot.copy_message(chat_info[1], message.chat.id, message.message_id)


if __name__ == "__main__":
    bot.infinity_polling('', skip_pending=True)
