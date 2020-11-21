Данный скрипт вдохновлён ежедневными публикациями Владимира Кондратьева в ФБ о ситуации с коронавирусом
в РФ и Москве, а также обсуждениями в комментариях про дополнительные данные.

Данные собираются с сайта [СтопКоронавирус.рф](https://xn--80aesfpebagmfblc0a.xn--p1ai/) и из 
[телеграм-канала Оперштаба Москвы](https://t.me/COVID2019_official).
В обоих случаях берутся последние доступные данные: на сайте они автоматически обновляются,
для телеграм-канала просматриваются последние 100 сообщений.

Надо иметь в виду, что программа заточена под формат данных на момент её написания.
Если форматирование сайта (или сообщения в телеграм канале) изменится, то данные получены не будут.
Если будет такое подозрение - обращайтесь к автору за правками (или поправьте сами!).

Для работы скрипта нужно следующее:

Подготовка:
===========
1) Установить Python 3-ей версии
2) Установить библиотеки `mechanicalsoup`, `BeautifulSoup`, `telethon`. Устанавливаются командой:
    ```shell script
    pip3 install telethon beautifulsoup4 MechanicalSoup
    ```
3) Файл `config_example.py` надо переименовать в `config.py` и заполнить указанные там данные (инструкция внутри файла)

Первый запуск:
==============
Запускаем скрипт:
```shell script
python3 main.py
```

При первом запуске телеграм-клиент залогинится (для этого спросит номер телефона, код подтверждения + пароль,
если включена двухэтапная авторизация).

После этого в локальной директории создастся файл `<Имя клиента>.session`, и в следующий раз логиниться в телеграм не
потребуется.

Дальше просто продолжаем запускать `python3 main.py`.

Enjoy!
