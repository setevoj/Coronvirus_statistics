# Модуль для парсинга данных из телеграм-канала оперштаба Москвы

from config import username, api_id, api_hash
from telethon import TelegramClient
from telethon.tl.functions.messages import (GetHistoryRequest)

moscow_covid_channel = 'https://t.me/COVID2019_official'
client = TelegramClient(username, api_id, api_hash)


MOSCOW_DATA_TAG = '️В Москве за сутки госпитализировали'


class MoscowData:
    def __init__(self, date, message_text):
        assert MOSCOW_DATA_TAG in message_text
        self.date = date
        # Берём данные из третьей строки
        words = message_text.splitlines()[2].split()
        # Вычленяем три числа из третьей строки
        self.infected, self.hospitalized, self.ventilated = [int(s) for s in words if s.isdigit()]


def get_messages(url, limit=100):
    """Get LIMIT messages from Telegram channel with given URL."""
    client = TelegramClient(username, api_id, api_hash)

    async def get_channel_data():
        nonlocal client
        channel = await client.get_entity(url)
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        return history.messages

    with client:
        return client.loop.run_until_complete(get_channel_data())


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
