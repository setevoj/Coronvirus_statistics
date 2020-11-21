from main import text2int


def test_text2int():
    assert text2int(['1', '231', '12 105', '106 789']) == [1, 231, 12_105, 106_789]
