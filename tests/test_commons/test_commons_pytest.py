import pytest
import sys
import datetime
sys.path.append('.')
from commons.commons import get_working_days_by_month

# command below will run all
# python3 -m nose

# command to run pytest
# pytest
# pytest tests/test_commons/test_commons_pytest.py -v


def test_if_date_a_working_day():

    rel = get_working_days_by_month('UK', 4)
    print(rel)
    assert datetime.date(2021, 4, 12) in rel, "Check April 12th is a working day, pass"

def test_if_date_is_holiday():

    rel = get_working_days_by_month('UK', 5)
    print(rel)
    assert datetime.date(2021, 4, 5) not in rel, "April 5th is a holiday, pass"
