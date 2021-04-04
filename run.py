from threading import Thread
from telegram import bot_start
from parse import parse
from current_serials import run_search_current_serials

def main():
    Thread(target= bot_start).start()
    #Thread(target=parse).start()
    #Thread(target=run_search_current_serials()).start()

main()


