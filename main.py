import json
import mechanicalsoup
from bs4 import BeautifulSoup

from moscow_data import extract_last_data, get_tginfo_message


# https://стопкоронавирус.рф/information/
STOP_CORONAVIRUS_URL = 'https://xn--80aesfpebagmfblc0a.xn--p1ai/information/'


def text2int(str_array):
    # Конвертируем массив текстовых форматированных записей в массив чисел.
    return [int(s.replace(' ', '')) if isinstance(s, str) else s
            for s in str_array]


RUSSIAN_DATA_FIELD_NAMES = ('sick', 'sickChange', 'healed', 'healedChange', 'died', 'diedChange')
REGION_DATA_FIELD_NAMES = ('sick', 'sick_incr', 'healed', 'healed_incr', 'died', 'died_incr')


class RegionData:
    def __init__(self, name, d, fields):
        """Capture COVID data for region NAME from a dict D.
        NAMES should be the names of the fields for sick, healed, and died, along with their daily changes."""
        self.name = name
        self.sick, self.sick_inc, self.healed, self.healed_inc, self.died, self.died_inc = text2int([
            d[fields[0]], d[fields[1]], d[fields[2]], d[fields[3]], d[fields[4]], d[fields[5]],
        ])
        self.active = self.sick - self.healed - self.died
        self.active_yesterday = self.active - self.sick_inc + self.healed_inc + self.died_inc
        self.inc_total_percentage = self.sick_inc / (self.sick - self.sick_inc) * 100.0
        self.inc_active_percentage = self.sick_inc / self.active_yesterday * 100

    def stats(self):
        """Return a line with stats for the region."""
        return (
            f"{self.name}: {self.sick_inc:+d} человек ({self.inc_total_percentage:+.2f}% от всех случаев, "
            f"{self.inc_active_percentage:+.2f}% от активных случаев), всего {self.sick:,}."
        )


def get_site_data(url):
    # Получаем данные с сайта
    browser = mechanicalsoup.StatefulBrowser()
    return parse_site_data(browser.open(url).text)


class Regions(dict):
    def stats(self, regions):
        return '\n'.join(self[r].stats() for r in regions)


def parse_site_data(text):
    """Extract RegionData from a web page text and return a dict region:RegionData."""
    soup = BeautifulSoup(text, features='lxml')

    regions_data = soup.find("cv-spread-overview")
    data = json.loads(regions_data.attrs[':spread-data'])

    regions_data = {x['title']: RegionData(x['title'], x, REGION_DATA_FIELD_NAMES) for x in data}

    # Russian data has a different set of field names
    ru_data = json.loads(soup.find("cv-stats-virus").attrs[":stats-data"])
    ru = RegionData('Россия', ru_data, RUSSIAN_DATA_FIELD_NAMES)

    return Regions({**regions_data, 'Россия': ru})


def print_data():
    print("Запрашиваем данные с сайта...")
    regions = get_site_data(STOP_CORONAVIRUS_URL)
    print("Данные с сайта получены.")

    print("Запрашиваем данные из телеграма...")
    tg_data = extract_last_data()
    print("Данные из телеграма получены.\n")

    print('Сформированное сообщение о ситуации:\n====================================\n')

    print("#коронавирус\n#официальныеданные\n#указаниясобянинавыполним\n")
    print(regions.stats(('Россия', 'Москва')))
    print(get_tginfo_message(*tg_data))


if __name__ == '__main__':
    print_data()



