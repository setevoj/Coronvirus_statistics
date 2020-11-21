import datetime
import pickle

from regions_data import text2int, RUSSIAN_DATA_FIELD_NAMES, REGION_DATA_FIELD_NAMES, RegionData, parse_site_data
from moscow_data import MoscowData, extract_last_data


def test_text2int():
    assert text2int(['1', '231', '12 105', '106 789']) == [1, 231, 12_105, 106_789]
    assert text2int([1, 231, '12105', 106_789]) == [1, 231, 12_105, 106_789]


def test_parse_site_data():
    regions = parse_site_data(open('fixtures/stop-corona.html').read())
    ru, mow = regions['Россия'], regions['Москва']
    # Russia
    assert ru.sick_inc == 24_318
    assert round(ru.inc_total_percentage, 2) == 1.21
    assert round(ru.inc_active_percentage, 2) == 5.36
    assert ru.sick == 2_039_926
    # Moscow
    assert mow.sick_inc == 6_902
    assert mow.sick == 539_970
    assert round(mow.inc_total_percentage, 2) == 1.29
    assert round(mow.inc_active_percentage, 2) == 5.05


def test_region_data():
    data = RegionData('Россия',
                      dict(sick=2_039_926, sickChange=24_318, healed=1_551_414, healedChange=24_758,
                           died=35_311, diedChange=461),
                      RUSSIAN_DATA_FIELD_NAMES)
    assert data.active == 453_201
    assert data.active - data.active_yesterday == -901

    data = RegionData('Москва',
                      dict(sick=539_970, sick_incr=6_902, healed=394_252, healed_incr=5_836,
                           died=8_159, died_incr=77),
                      REGION_DATA_FIELD_NAMES)
    assert data.active == 137_559


def test_regions_stats():
    regions = parse_site_data(open('fixtures/stop-corona.html').read())
    assert regions.stats(['Россия', 'Москва']) == (
        'Россия: +24318 человек (+1.21% от всех случаев, +5.36% от активных случаев), всего 2,039,926.\n'
        'Москва: +6902 человек (+1.29% от всех случаев, +5.05% от активных случаев), всего 539,970.')


def test_parse_opershtab_message():
    message = """❗️В Москве за сутки госпитализировали 1489 пациентов с коронавирусом

В столице подтверждено 6902 новых случая заражения коронавирусной инфекцией. За последние сутки госпитализировано 1489 пациентов с COVID-19. На ИВЛ в больницах Москвы находятся 423 человека.

Среди новых выявленных случаев:

🔹42,2%— от 18 до 45 лет
🔹31,9%— от 46 до 65 лет
🔹8,9%— от 66 до 79 лет
🔹3,4% — старше 80 лет
🔹13,6% — дети

Оперштаб напоминает о необходимости соблюдения домашнего режима горожанам старше 65 лет и москвичам с хроническими заболеваниями."""
    today = datetime.date.today()
    data = MoscowData(today, message)
    assert data.date == today
    assert data.infected == 6_902
    assert data.hospitalized == 1_489
    assert data.ventilated == 423


def test_extract_last_data():
    # We've created messages.pickle by running the following commands:
    #   import pickle
    #   import telegram
    #   pickle.dump(telegram.get_messages('https://t.me/COVID2019_official'), open('fixtures/messages.pickle', 'wb'))
    messages = pickle.load(open('fixtures/messages.pickle', 'rb'))
    hospitalized, ventilated, hosp_inc, vent_inc, last_available_date = extract_last_data(messages)
    assert hospitalized == 1_535
    assert hosp_inc == 46
    assert ventilated == 419
    assert vent_inc == -4
    assert last_available_date == datetime.date(2020, 11, 21)
