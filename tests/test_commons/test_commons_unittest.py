import unittest

# command below will run this test
# python3 -m unittest discover -s tests

# command below will run all
# python3 -m nose

# command pytest
# python3 -m pytest
import datetime
import sys
sys.path.append('.')
from commons.commons import get_working_days_by_month


class TestIfWorkingDay(unittest.TestCase):
    def test_is_working_day(self):
        """
        Check April 12th is a working day, pass
        """
        rel = get_working_days_by_month('UK', 4)
        self.assertTrue(datetime.date(2021, 4, 12) in rel)


if __name__ == '__main__':
    unittest.main()