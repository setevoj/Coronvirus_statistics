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


def get_opershtab_db(messages=None):
    if not messages:
        messages = get_messages(MOSCOW_COVID_CHANNEL, 100)
    return [MoscowData(m.date.date(), m.raw_text) for m in messages if MOSCOW_DATA_TAG in m.raw_text]


def extract_last_data(db):
    # Вычленяем данные оперштаба Москвы за последнюю доступную дату из общей базы
    # Возвращаем данные за сегодняшнее число (или None, если таких данных не найдено), а также прирост/убыль
    # госпитализаций и людей на аппаратах ИВЛ по сравнению с предыдущим днём
    if len(db) == 0:
        return [None] * 5

    last = db[0]
    prev = db[1] if len(db) > 1 and last.date - db[1].date == timedelta(days=1) else None
    if prev:
        return (
            last.hospitalized, last.ventilated,
            last.hospitalized-prev.hospitalized, last.ventilated-prev.ventilated,
            last.date)
    else:
        return (
            last.hospitalized, last.ventilated,
            None, None,
            last.date)


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