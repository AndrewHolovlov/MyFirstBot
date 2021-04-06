import os
import telebot
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

token = os.environ.get("TOKEN")
bot = telebot.TeleBot(token)
print(bot.get_me())


def bot_start():
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(f"Error.polling: {e}")


