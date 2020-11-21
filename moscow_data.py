# Модуль для парсинга данных из телеграм-канала оперштаба Москвы
from datetime import timedelta, datetime

from telegram import get_messages

MOSCOW_COVID_CHANNEL = 'https://t.me/COVID2019_official'


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
    for message in get_messages(MOSCOW_COVID_CHANNEL, 100):
        if '️В Москве за сутки госпитализировали' in message.raw_text:
            # Берём данные из третьей строки
            words = message.raw_text.splitlines()[2].split()
            # Вычленяем три числа из третьей строки
            infected, hospitalized, ventilated = [int(s) for s in words if s.isdigit()]
            database.append([message.date, infected, hospitalized, ventilated])
    return database


def extract_last_data(db):
    # Вычленяем данные оперштаба Москвы за последнюю доступную дату из общей базы
    # Возвращаем данные за сегодняшнее число (или None, если таких данных не найдено), а также прирост/убыль
    # госпитализаций и людей на аппаратах ИВЛ по сравнению с предыдущим днём
    if not db:
        return [None] * 5

    # Данные отсортированы в обратном хронологическом порядке, поэтому первая запись самая актуальная
    last_available_record = db[0]
    last_available_date = last_available_record[0].date()  # Дата на первом месте, берём без времени
    hospitalized = last_available_record[2]
    ventilated = last_available_record[3]

    # Пробуем получить данные за предыдущую дату
    previous_date = last_available_date - timedelta(days=1)
    if len(db) > 1 and db[1][0].date() == previous_date:  # Если есть данные за две даты и
        # если предыдущая дата была перед последней
        previous_record = db[1]
    else:
        previous_record = []

    if previous_record:  # Есть данные за вчера
        hosp_inc = hospitalized - previous_record[2]
        vent_inc = ventilated - previous_record[3]
    else:
        hosp_inc, vent_inc = [None] * 2

    return hospitalized, ventilated, hosp_inc, vent_inc, last_available_date


def get_tginfo_message(*args):
    hospitalized, ventilated, hosp_inc, vent_inc, data_date = args

    # Формируем правильное имя для дня по которому есть данные в телеграме
    if data_date is None:
        day_name = 'последнее время'
    elif data_date == datetime.today().date():
        day_name = "вчера"
    elif data_date == datetime.today().date() - timedelta(days=1):
        day_name = "позавчера"
    else:
        day_name = data_date.strftime("%m.%d.%Y")

    if hospitalized is not None:
        message = f"Число госпитализированных в Москве за {day_name}: {hospitalized}"
        if hosp_inc is not None:
            message += f" ({hosp_inc:+d} к предыдущему дню).\n"
        else:
            message += "(данных за предыдущий день нет).\n"
        message += f"Число больных на ИВЛ в Москве за {day_name}: {ventilated}"
        if vent_inc is not None:
            message += f" ({vent_inc:+d} к предыдущему дню)."
        else:
            message += "(данных за предыдущий день нет)."
    else:
        message = f"Нет данных по госпитализациям в Москве за {day_name}."
        message += f"\nНет данных по больным на ИВЛ в Москве за {day_name}."

    return message