from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from main import get_html
from db import User, Serial

engine = create_engine('postgresql://postgres:0627@localhost:5432/db')
base = declarative_base()
base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()

URL = "https://rezka.ag/"
HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36', 'accept':'*/*' }

def search_current_serials(html = get_html(URL)):
    if html.status_code == 200:
        html = html.text
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('li', class_='b-seriesupdate__block_list_item')
        for item in items:
            name = item.find('a', class_='b-seriesupdate__block_list_link')
            if name != None:
                name = name.get_text()
                if session.query(Serial).filter(Serial.name == name.lower()).first() == None:
                    session.add(Serial(name = name.lower()))
        session.commit()
    else:
        print("Error status_code")

search_current_serials()

