import time
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from parse import get_html
from db import User, Serial, session


URL = "https://rezka.ag/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
    'accept': '*/*'}


def search_current_serials(html=get_html(URL)):
    if html.status_code == 200:
        html = html.text
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('li', class_='b-seriesupdate__block_list_item')
        for item in items:
            name = item.find('a', class_='b-seriesupdate__block_list_link')
            if name != None:
                name = name.get_text()
                if session.query(Serial).filter(Serial.name == name).first() == None:
                    session.add(Serial(name=name))
        session.commit()
    else:
        print("Error status_code")
    print("search_current_serials")


def run_search_current_serials():
    while True:
        try:
            search_current_serials()
            time.sleep(3600)
        except:
            print("Erro.search_current_serials")

def search_serials(serial_name, user):
    search = serial_name.replace(" ", "+")
    url = 'https://rezka.ag/search/?do=search&subaction=search&q='+ search
    print(url)
    html = get_html(url)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find_all('div', class_='b-content__inline_item')
        for item in items:
            if item.find('i', class_='entity').get_text() == 'Сериал':
                name = item.find('div', class_='b-content__inline_item-link').find('a').get_text()
                print(name)
                if name.lower() == serial_name.lower():
                    serial = Serial(name = serial_name)
                    session.add(serial)
                    user.serials.append(serial)
                    session.commit()
                    return True
        return False
    else:
        print("Error: earch_serials - status_code")


# def search_serials(serial_name, user):
#     i = 1
#     while True:
#         print(i)
#         url = "https://rezka.ag/series/page/" + str(i) + "/"
#         html = get_html(url)
#         if html.status_code == 200:
#             soup = BeautifulSoup(html.text, 'html.parser')
#             items = soup.find_all('div', class_='b-content__inline_item-link')
#             for item in items:
#                 name = item.find('a')
#                 if name.get_text() == serial_name:
#                     serial = Serial(name = name.get_text)
#                     session.add(serial)
#                     user.serials.append(serial)
#                     #session.commit()
#                     print("True")
#                     return True
#         elif html.status_code == 404:
#             break
#         else:
#             print("Error: search_serials - status_code: " + str(html.status_code))
#         i = i + 1