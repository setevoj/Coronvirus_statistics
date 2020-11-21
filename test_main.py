from main import text2int, parse_site_data


def test_text2int():
    assert text2int(['1', '231', '12 105', '106 789']) == [1, 231, 12_105, 106_789]


def test_parse_site_data():
    with open('./stop-corona.html', 'r') as f:
        ru_sick_inc, ru_inc_total_percentage, ru_inc_active_percentage, ru_sick, mow_sick_inc, \
            mow_inc_total_percentage, mow_inc_active_percentage, mow_sick = \
            parse_site_data(f.read())
    # Russia
    assert ru_sick_inc == 24_318
    assert round(ru_inc_total_percentage, 2) == 1.21
    assert round(ru_inc_active_percentage, 2) == 5.36
    assert ru_sick == 2_039_926

    # Moscow
    assert mow_sick_inc == 6_902
    assert mow_sick == 539_970
    assert round(mow_inc_total_percentage, 2) == 1.29
    assert round(mow_inc_active_percentage, 2) == 5.05
