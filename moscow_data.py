# Модуль для парсинга данных из телеграм-канала оперштаба Москвы
from telegram import get_messages

moscow_covid_channel = 'https://t.me/COVID2019_official'


MOSCOW_DATA_TAG = '️В Москве за сутки госпитализировали'


class MoscowData:
    def __init__(self, date, message_text):
        assert MOSCOW_DATA_TAG in message_text
        self.date = date
        # Берём данные из третьей строки
        words = message_text.splitlines()[2].split()
        # Вычленяем три числа из третьей строки
        self.infected, self.hospitalized, self.ventilated = [int(s) for s in words if s.isdigit()]


def get_opershtab_db():
    database = []
    for message in get_messages(moscow_covid_channel, 100):
        if '️В Москве за сутки госпитализировали' in message.raw_text:
            # Берём данные из третьей строки
            words = message.raw_text.splitlines()[2].split()
            # Вычленяем три числа из третьей строки
            infected, hospitalized, ventilated = [int(s) for s in words if s.isdigit()]
            database.append([message.date, infected, hospitalized, ventilated])
    return database
