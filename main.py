from moscow_data import extract_last_data, get_tginfo_message
from regions_data import get_site_data


def print_data():
    print("Запрашиваем данные с сайта...")
    regions = get_site_data()
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



