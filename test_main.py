from main import (
    text2int, parse_site_data, get_site_info_message,
    RegionData, RUSSIAN_DATA_FIELD_NAMES, REGION_DATA_FIELD_NAMES
)


def test_text2int():
    assert text2int(['1', '231', '12 105', '106 789']) == [1, 231, 12_105, 106_789]
    assert text2int([1, 231, '12105', 106_789]) == [1, 231, 12_105, 106_789]


def test_parse_site_data():
    regions = parse_site_data(open('./stop-corona.html').read())
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


def test_get_site_info_message():
    site_data = parse_site_data(open('./stop-corona.html').read())
    assert get_site_info_message(site_data) == (
        'Россия: +24318 человек (+1.21% от всех случаев, +5.36% от активных случаев), всего 2,039,926.\n'
        'Москва: +6902 человек (соответственно +1.29% , +5.05%), всего 539,970.')
