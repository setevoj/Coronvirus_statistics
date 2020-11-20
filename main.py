import json
import mechanicalsoup
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
import get_telegram_data


def text2int(str_array):
    # Конвертируем массив текстовых форматированных записей в массив чисел
    result = []
    for str in str_array:
        result.append(int(str.replace(" ", "")))
    return result


def get_site_data():
    # Получаем данные с сайта
    browser = mechanicalsoup.StatefulBrowser()
    soup = BeautifulSoup(browser.open('https://xn--80aesfpebagmfblc0a.xn--p1ai/information/').text, features='lxml')

    # Данные по Москве
    ru_data = json.loads(soup.find("cv-stats-virus").attrs[":stats-data"])
    ru_sick, ru_sick_inc, ru_healed, ru_healed_inc, ru_died, ru_died_inc = text2int([ru_data['sick'],
                                                                                     ru_data['sickChange'],
                                                                                     ru_data['healed'],
                                                                                     ru_data['healedChange'],
                                                                                     ru_data['died'],
                                                                                     ru_data['diedChange']])

    ru_active = ru_sick - ru_healed - ru_died
    ru_active_yesterday = ru_active - ru_sick_inc + ru_healed_inc + ru_died_inc
    ru_inc_total_percentage = ru_sick_inc / (ru_sick - ru_sick_inc) * 100
    ru_inc_active_percentage = ru_sick_inc / (ru_active_yesterday) * 100

    # Данные по региону
    regions_data = soup.find("cv-spread-overview")  # and tag.has_attr('id') and tag['id'] == "Table1")
    data = json.loads(regions_data.attrs[':spread-data'])
    mow_data = [x for x in data if x['title'] == 'Москва'][0]
    mow_sick, mow_sick_inc, mow_healed, mow_healed_inc, mow_died, mow_died_inc = [mow_data['sick'],
                                                                                  mow_data['sick_incr'],
                                                                                  mow_data['healed'],
                                                                                  mow_data['healed_incr'],
                                                                                  mow_data['died'],
                                                                                  mow_data['died_incr']]
    mow_active = mow_sick - mow_healed - mow_died
    mow_active_yesterday = mow_active - mow_sick_inc + mow_healed_inc + mow_died_inc
    mow_inc_total_percentage = mow_sick_inc / (mow_sick - mow_sick_inc) * 100
    mow_inc_active_percentage = mow_sick_inc / (mow_active_yesterday) * 100

    return ru_sick_inc, ru_inc_total_percentage, ru_inc_active_percentage, ru_sick, \
           mow_sick_inc, mow_inc_total_percentage, mow_inc_active_percentage, mow_sick


def extract_last_data(db):
    # Вычленяем данные оперштаба Москвы за последнюю доступную дату из общей базы
    # Возвращаем данные за сегодняшнее число (или None, если таких данных не найдено), а также прирост/убыль
    # госпитализаций и людей на аппаратах ИВЛ по сравнению с предыдущим днём
    if not db:
        return [None] * 5

    # Данные отсортированы в обратном хронологическом порядке, поэтому первая запись самая актуальная
    last_available_record = db[0]
    last_available_date = last_available_record[0].date() # Дата на первом месте, берём без времени
    hospitalized = last_available_record[2]
    ventilated = last_available_record[3]

    # Пробуем получить данные за предыдущую дату
    previous_date = last_available_date - timedelta(days=1)
    if len(db) > 1 and db[1][0].date() == previous_date: # Если есть данные за две даты и
                                                        # если предыдущая дата была перед последней
        previous_record = db[1]
    else:
        previous_record = []

    if previous_record: # Есть данные за вчера
        hosp_inc = hospitalized - previous_record[2]
        vent_inc = ventilated - previous_record[3]
    else:
        hosp_inc, vent_inc = [None] * 2

    return hospitalized, ventilated, hosp_inc, vent_inc, last_available_date


def get_siteinfo_message(*args):
    ru_sick_inc, ru_inc_total_percentage, ru_inc_active_percentage, ru_sick, \
    mow_sick_inc, mow_inc_total_percentage, mow_inc_active_percentage, mow_sick = args
    return  f"Россия: {ru_sick_inc:+d} человек ({ru_inc_total_percentage:+.2f}% от всех случаев, " \
            f"{ru_inc_active_percentage:+.2f}% от активных случаев), всего {ru_sick:,}.\n" \
            f"Москва: {mow_sick_inc:+d} человек (соответственно {mow_inc_total_percentage:+.2f}% , " \
            f"{mow_inc_active_percentage:+.2f}%), всего {mow_sick:,}."


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


def print_data():
    print("Запрашиваем данные с сайта...")
    site_data = get_site_data()
    print("Данные с сайта получены.")

    print("Запрашиваем данные из телеграма...")
    db = get_telegram_data.get_opershtab_db()
    # Берём данные за последний доступный день
    tg_data = extract_last_data(db)
    print("Данные из телеграма получены.\n")

    print("Сформированное сообщение о ситуации:\n====================================\n")

    print("#коронавирус\n#официальныеданные\n#указаниясобянинавыполним\n")
    print(get_siteinfo_message(*site_data) + '\n' + get_tginfo_message(*tg_data))


if __name__ == '__main__':
    print_data()



