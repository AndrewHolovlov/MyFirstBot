import requests
from bs4 import BeautifulSoup
import json

tv_series = {"Ходячие мертвецы": [],
 "Бумажный дом": []}


URL = "https://rezka.ag/"
HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36', 'accept':'*/*' }


def get_html(url):
    r = requests.get(url, headers=HEADERS)
    return  r

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('li', class_='b-seriesupdate__block_list_item')
    for key in tv_series:
        for item in items:
            name = item.find('a', class_='b-seriesupdate__block_list_link')
            if name != None:
                name = name.get_text()
            if name == key:
                tv_series[key].append(item.find('span', class_='season').get_text() +" "+ item.find('span', class_='cell cell-2').get_text())

def parse():
    html = get_html(URL)
    if html.status_code == 200:
        get_content(html.text)
    else:
        print("Error status_code")
