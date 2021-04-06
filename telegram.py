from bs4 import BeautifulSoup
from sqlalchemy import types, func
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
from db import User, Serial, session
from new_episodes import get_html


a = KeyboardButton("Добавить сериал")
# s = KeyboardButton("Поиск обновлений за последние сутки")
m = KeyboardButton("Мои сериалы")
d = KeyboardButton("Удалить сериал")
main_markup = ReplyKeyboardMarkup(True, True).add(a).add(m).add(d)


@bot.message_handler(commands=['start'])
def send_message(message):
    if session.query(User.telegram_id).filter(User.telegram_id == str(message.from_user.id)).first() == None:
        user = User(telegram_id=message.from_user.id, user_name_telegram=message.from_user.username)
        session.add(user)
        session.commit()
        bot.send_message(message.chat.id, "Привет, мое имя bot", reply_markup=main_markup)
    else:
        bot.send_message(message.chat.id, "Мы уже знакомы")


@bot.message_handler(commands=['button'])
def send_message(message):
    bot.send_message(message.chat.id, "Вот твои кнопки)", reply_markup=main_markup)


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
    search = message.text.replace(" ", "+")
    url = 'https://rezka.ag/search/?do=search&subaction=search&q=' + search
    print(url)
    html = get_html(url)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find_all('div', class_='b-content__inline_item')
        serials = []
        for item in items:
            if item.find('i', class_='entity').get_text() == 'Сериал':
                serials.append(item)
        if len(serials) >= 3:
            serials = serials[:3]
        markup = InlineKeyboardMarkup()
        for item in serials:
            name = item.find('div', class_='b-content__inline_item-link').find('a').get_text()
            print(name)
            callback_button = InlineKeyboardButton(text=name, callback_data=name[0:30])
            # callback_button = InlineKeyboardButton(text=name, callback_data={'add': name[0:30]})
            markup.add(callback_button)
        callback_button = InlineKeyboardButton(text="Отмена", callback_data="Отмена")
        markup.add(callback_button)
        bot.send_message(message.chat.id, "Выбери свой сериал\nЕсли его здесь нет попробуй еще раз", reply_markup=markup)
    else:
        print("Error: earch_serials - status_code -" + str(html.status_code))

def delete(message):
    user = session.query(User).filter(User.telegram_id == str(message.from_user.id)).first()
    if user != None:
        if len(user.serials.all()) > 0:
            serial = session.query(Serial).filter(func.lower(Serial.name) == func.lower(message.text)).first()
            if serial != None:
                user.serials.remove(serial)
                session.commit()
                bot.send_message(message.chat.id, "Сериал был успешно удален")
            else:
                bot.send_message(message.chat.id, "Извини, но такого сериала нет, попробуйте еще раз")
        else:
            bot.send_message(message.chat.id, "Вы еще не добавили сериалы, воспользуйтесь командой add")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        # if hasattr(call.data, 'add'):
        #     serial_name = call.data['add']
        if call.data == "Отмена":
            bot.send_message(call.message.chat.id, "Если вы не нашли свой сериал в списке попробуйте еще раз")
        else:
            user = session.query(User).filter(User.telegram_id == str(call.message.chat.id)).first()
            if user != None:
                serial = session.query(Serial).filter(Serial.name == call.data).first()
                if serial == None:
                    serial = Serial(name=call.data)
                    session.add(serial)
                    user.serials.append(serial)
                    session.commit()
                    bot.send_message(call.message.chat.id, "Сериал был успешно добавлен")
                else:
                    if serial in user.serials.all():
                        bot.send_message(call.message.chat.id, "У вас уже есть такой сериал")
                    else:
                        user.serials.append(serial)
                        session.commit()
                        bot.send_message(call.message.chat.id, "Сериал был успешно добавлен")
    bot.delete_message(call.message.chat.id, call.message.message_id)
