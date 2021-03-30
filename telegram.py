import json
import telebot
from sqlalchemy import create_engine, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from db import User, Serial
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

token = os.environ.get("TOKEN")
db_path = os.environ.get("DB_PATH")
password = os.environ.get("PASS")


engine = create_engine('postgresql://postgres:' + password + '@' + db_path)
base = declarative_base()
base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

bot = telebot.TeleBot(token)

a = KeyboardButton("Добавить сериал")
s = KeyboardButton("Поиск обновлений за последние сутки")
m = KeyboardButton("Мои сериалы")
d = KeyboardButton("Удалить сериал")
markup = ReplyKeyboardMarkup(True, True).add(a).add(s).add(m).add(d)

@bot.message_handler(commands=['start'])
def send_message(message):
    if session.query(User.telegram_id).filter(User.telegram_id == str(message.from_user.id)).first() == None:
        user = User(telegram_id=message.from_user.id, user_name_telegram=message.from_user.username)
        session.add(user)
        session.commit()
        bot.send_message(message.chat.id, "Привет, мое имя bot", reply_markup = markup)
    else:
        bot.send_message(message.chat.id, "Мы уже знакомы")

@bot.message_handler(commands=['button'])
def send_message(message):
    bot.send_message(message.chat.id, "Вот твои кнопки)", reply_markup=markup)

@bot.message_handler(commands=['help'])
def send_message(message):
    send = "Привет мое имя bot\n\nЯ тебе расскажу про обновление по твоим любимым сериалам\n\nВведи:\n\n\t/start - чтобы познакомится со мной\n\n\t/button - получить набор кнопок, чтобы тебе было легче со мной общаться\n\n\tДобавить сериал - чтобы добавить сериал\n\n\tУдалить сериал - чтобы удалить сериал\n\n\tМои сериалы - посмотреть список своих сериаловn\n\n\tПоиск обновлений за последние сутки - посмотреть обновление по сериалам за последние сутки"
    bot.send_message(message.chat.id, send)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if session.query(User).filter(User.telegram_id == str(message.from_user.id)).first() != None:
        if message.text.lower() == "Добавить сериал".lower():
            bot.send_message(message.chat.id, "Введите имя сериала")
            try:
                bot.register_next_step_handler(message, add)
            except:
                bot.send_message(message.chat.id, "Произошла ошибка, попробуйте еще раз")

        elif message.text.lower() == 'Удалить сериал'.lower():
            bot.send_message(message.chat.id, "Введите имя сериала который хотите удалить")
            try:
                bot.register_next_step_handler(message, delete)
            except:
                bot.send_message(message.chat.id, "Произошла ошибка, попробуйте еще раз")

        elif message.text.lower() == 'Поиск обновлений за последние сутки'.lower():
            with open('serial.json', 'r') as j:
                data = json.load(j)
            user = session.query(User).filter(User.telegram_id == str(message.from_user.id)).first()
            if user != None:
                serials = user.serials.all()
                if len(serials) > 0:
                    s = "Обновление за последние сутки:\n"
                    for serial in serials:
                        s += serial.name + ":\n"
                        for item in data[serial.name]:
                            s += "\t" + item + "\n"
                    bot.send_message(message.chat.id, s)
                else:
                    bot.send_message(message.chat.id, "Вы еще не добавили сериалы, воспользуйтесь командой add")

        elif message.text.lower() == 'Мои сериалы'.lower():
            user = session.query(User).filter(User.telegram_id == str(message.from_user.id)).first()
            if user != None:
                serials = user.serials.all()
                if len(serials) > 0:
                    s = "Ваши сериалы:\n"
                    for serial in serials:
                        s += serial.name + "\n"
                    bot.send_message(message.chat.id, s)
                else:
                    bot.send_message(message.chat.id, "Вы еще не добавили сериалы, воспользуйтесь командой add")
        else:
            bot.send_message(message.chat.id, "Извините, но я не знаю такой команды(")
    else:
        bot.send_message(message.chat.id, "Привет мы с тоюой еще не знакомы, для начала введи команду /start")

def add(message):
    serial = session.query(Serial).filter(Serial.name == message.text).first()
    if serial != None:
        user = session.query(User).filter(User.telegram_id == str(message.from_user.id)).first()
        if user != None:
            if serial in user.serials.all():
                bot.send_message(message.chat.id, "У вас уже есть такой сериал")
            else:
                user.serials.append(serial)
                session.commit()
                bot.send_message(message.chat.id, "Сериал был успешно добавлен")
    else:
        bot.send_message(message.chat.id, "Извини, но такого сериала нет, попробуйте еще раз")

def delete(message):
    user = session.query(User).filter(User.telegram_id == str(message.from_user.id)).first()
    if user != None:
        if len(user.serials.all()) > 0:
            serial = session.query(Serial).filter(Serial.name == message.text.lower()).first()
            if serial != None:
                user.serials.remove(serial)
                session.commit()
                bot.send_message(message.chat.id, "Сериал был успешно удален")
            else:
                bot.send_message(message.chat.id, "Извини, но такого сериала нет, попробуйте еще раз")
        else:
            bot.send_message(message.chat.id, "Вы еще не добавили сериалы, воспользуйтесь командой add")


def bot_start():
    while True:
        try:
            bot.polling()
        except:
            print("Error.polling")