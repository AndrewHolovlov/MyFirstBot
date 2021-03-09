import json
import telebot
from sqlalchemy import create_engine, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from main import parse, tv_series
from db import User, Serial

engine = create_engine('postgresql://postgres:0627@localhost:5432/db')
base = declarative_base()
base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

bot = telebot.TeleBot('1519055784:AAEGy61wWj1i75UN72RAxz5rrR3VMKdMfw4')

a = KeyboardButton("add")
s = KeyboardButton("search")
markup = ReplyKeyboardMarkup(True, True).add(a).add(s)

@bot.message_handler(commands=['start'])
def send_message(message):
    if session.query(User.telegram_id).filter(User.telegram_id == str(message.from_user.id)).first() == None:
        user = User(telegram_id=message.from_user.id, user_name_telegram=message.from_user.username)
        session.add(user)
        session.commit()
        bot.send_message(message.chat.id, "Привет, мое имя bot", reply_markup = markup)
    else:
        bot.send_message(message.chat.id, "Мы уже знакомы")


@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'add':
        bot.send_message(message.chat.id, "Введите имя сериала")
        bot.register_next_step_handler(message, add)
    elif message.text.lower() == 'serials':
        names = session.query(Serial.name).all()
        for name in names:
            bot.send_message(message.chat.id, name.name)

def add(message):
    serial = session.query(Serial).filter(Serial.name == message.text.lower()).first()
    if  serial != None:
        user = session.query(User).filter(User.telegram_id == str(message.from_user.id)).first()
        if user != None:
            if serial in user.serials.all():
                bot.send_message(message.chat.id, "У вас уже есть такой сериал")
            else:
                user.serials.append(serial)
                session.commit()
        else:
            bot.send_message(message.chat.id, "Привет, мы с тобой еще не знакомы\nВведи команду /start")
    else:
        bot.send_message(message.chat.id, "Извини, но такого сериала нет")



bot.polling()