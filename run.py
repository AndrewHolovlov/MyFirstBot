from threading import Thread
from bot import bot_start
from new_episodes import run_parse


def main():
    Thread(target=bot_start).start()
    Thread(target=run_parse).start()


main()


