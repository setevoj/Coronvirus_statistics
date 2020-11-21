# Модуль для парсинга данных из телеграм-канала оперштаба Москвы

from config import username, api_id, api_hash
from telethon import TelegramClient
from telethon.tl.functions.messages import (GetHistoryRequest)

moscow_covid_channel = 'https://t.me/COVID2019_official'
client = TelegramClient(username, api_id, api_hash)


async def get_channel_data():
    opershtab_channel = await client.get_entity(moscow_covid_channel)

    database = []  # Сюда будем писать данные по датам

    history = await client(GetHistoryRequest(
        peer=opershtab_channel,
        offset_id=0,
        offset_date=None,
        add_offset=0,
        limit=100,
        max_id=0,
        min_id=0,
        hash=0
    ))
    if not history.messages:
        return "Нет сообщений в канале оперштаба!"

    messages = history.messages
    for message in messages:
        if '️В Москве за сутки госпитализировали' in message.raw_text:
            # Берём данные из третьей строки
            words = message.raw_text.splitlines()[2].split()
            # Вычленяем три числа из третьей строки
            infected, hospitalized, ventilated = [int(s) for s in words if s.isdigit()]
            database.append([message.date, infected, hospitalized, ventilated])

    return database


def get_opershtab_db():
    # Запускаем в асинхронном режиме
    with client:
        database = client.loop.run_until_complete(get_channel_data())
    return database


def print_opershtab_db(database):
    # Печатаем базу данных
    for data in database:
        print(f"Данные на дату {data[0].strftime('%d-%m-%Y')}: Заражено {data[1]}, "
              f"госпитализировано {data[2]}, на ИВЛ: {data[3]}")
