import time
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db import User, Serial
import json

engine = create_engine('postgresql://postgres:0627@localhost:5432/db')
base = declarative_base()
base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

URL = "https://rezka.ag/"
HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36', 'accept':'*/*' }

def get_html(url):
    r = requests.get(url, headers=HEADERS)
    return  r

def parse():
    html = get_html(URL)
    if html.status_code == 200:
        get_content(html.text)
    else:
        print("Error status_code")
    print("parse")

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    block = soup.find('div', class_='b-seriesupdate__block')
    items = block.find_all('li', class_='b-seriesupdate__block_list_item')
    tv = {}
    serials = session.query(Serial).all()
    for serial in serials:
        tv[serial.name] = []
        for item in items:
            name = item.find('a', class_='b-seriesupdate__block_list_link')
            if name != None:
                name = name.get_text()
                if name == serial.name:
                    tv[serial.name].append(item.find('span', class_='season').get_text() +" "+ item.find('span', class_='cell cell-2').get_text())
        if len(tv[serial.name]) == 0:
            tv[serial.name].append("За последнии сутки обновлений не было")
    print(tv)
    with open('serial.json', 'w') as j:
        json.dump(tv, j)

def run_parse():
    while True:
        try:
            parse()
            time.sleep(3600)
        except:
            print("Error.parse")