import json
import telebot
from sqlalchemy import create_engine, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from db import User, Serial

engine = create_engine('postgresql://postgres:0627@localhost:5432/db')
base = declarative_base()
base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

bot = telebot.TeleBot('1519055784:AAEGy61wWj1i75UN72RAxz5rrR3VMKdMfw4')

a = KeyboardButton("add")
s = KeyboardButton("search")
m = KeyboardButton("my serials")
d = KeyboardButton("delete")
markup = ReplyKeyboardMarkup(True, True).add(a).add(s).add(m).add(d)

@bot.message_handler(commands=['start'])
def send_message(message):
    bot.send_message(message.chat.id, "button", reply_markup=markup)
    if session.query(User.telegram_id).filter(User.telegram_id == str(message.from_user.id)).first() == None:
        user = User(telegram_id=message.from_user.id, user_name_telegram=message.from_user.username)
        session.add(user)
        session.commit()
        bot.send_message(message.chat.id, "Привет, мое имя bot", reply_markup = markup)
    else:
        bot.send_message(message.chat.id, "Мы уже знакомы")


@bot.message_handler(content_types=['text'])
def send_text(message):
    if session.query(User).filter(User.telegram_id == str(message.from_user.id)).first() != None:
        if message.text.lower() == 'add':
            bot.send_message(message.chat.id, "Введите имя сериала")
            try:
                bot.register_next_step_handler(message, add)
            except:
                bot.send_message(message.chat.id, "Произошла ошибка, попробуйте еще раз")

        elif message.text.lower() == 'delete':
            bot.send_message(message.chat.id, "Введите имя сериала который хотите удалить")
            try:
                bot.register_next_step_handler(message, delete)
            except:
                bot.send_message(message.chat.id, "Произошла ошибка, попробуйте еще раз")

        elif message.text.lower() == 'search':
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

        elif message.text.lower() == 'my serials':
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
    serial = session.query(Serial).filter(Serial.name == message.text.lower()).first()
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

bot.polling()