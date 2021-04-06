import requests
from bs4 import BeautifulSoup
import time

from db import User, Serial, session
from bot import bot


URL = "https://rezka.ag/"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36', 'accept':'*/*' }


def get_html(url):
    r = requests.get(url, headers=HEADERS)
    return r


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        new_episodes(html.text)
    else:
        print("Error status_code")
    print("new episodes")


def new_episodes(html):
    """
    Parse shows updates from HDrezka and send them to users
    User receives updates only for those shows to which he is subscribed
    """
    soup = BeautifulSoup(html, 'html.parser')
    item = soup.find('div', class_='b-seriesupdate__block_list_item_inner')
    key = item.find('a', class_='b-seriesupdate__block_list_link').get_text()
    content = item.find('span', class_='season').get_text() + " " + item.find('span', class_='cell cell-2').get_text()
    print(key + " " + content)
    for user in session.query(User).all():
        serials = user.serials.all()
        if session.query(Serial).filter(Serial.name == key).first() in serials:
            if (user.key != key and user.content != content) or (user.key == key and user.content != content):
                bot.send_message(user.telegram_id, key + "\n" + content)
                user.key = key
                user.content = content
                session.commit()


def run_parse():
    while True:
        try:
            parse()
            time.sleep(120)
        except:
            print("Error: run_parse")

