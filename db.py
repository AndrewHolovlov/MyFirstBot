from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import json
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, raiseload
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm.strategy_options import lazyload

engine = create_engine('postgresql://postgres:0627@localhost:5432/db')
base = declarative_base()

class User(base):
    __tablename__ ='users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String)
    user_name_telegram = Column(String)
    serials = relationship("Serial", backref = "user", lazy ='dynamic')

class Serial(base):
    __tablename__='serials'
    id = Column(Integer, primary_key=True)
    id_user = Column(Integer, ForeignKey('users.id'))
    name = Column(String)



base.metadata.create_all(engine)

session = sessionmaker(bind=engine)()

#s1 = Serial(name= "Ходячие мертвецы")
#s2 = Serial(name= "Бумажный дом")

#u = User(telegram_id="one", user_name_telegram= "one")

#u.serials.append(s1)
#u.serials.append(s2)

#session.add_all([s1, s2, u])

#users = session.query(User).all()

#for user in users:
    #for item in user.serials.all():
        #print(item.name)

#query = session.query(User.telegram_id).filter(User.telegram_id == "fsdfs").first()
#print(query)

#for item in session.query(Serial).all():
    #session.delete(item)
    #print(item.telegram_id + " " + item.user_name_telegram)

#session.commit()

#names = session.query(Serial.name).all()

#print(names)

'''for item in session.query(User).all():
    session.delete(item)

session.commit()'''

#for serial in session.query(Serial).all():
    #print(serial.name)