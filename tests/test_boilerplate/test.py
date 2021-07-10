# command below will run this test
# python3 -m unittest discover -s tests

# command below will run all
# python3 -m nose

# command pytest
# python3 -m pytest

import unittest
import sys

sys.path.append('.')
from commons.commons import write_test_result_json
from commons.commons import read_test_result_json


class DoSomething(unittest.TestCase):
    def test_do_something(self):
        dic = {"Result": "abc"}
        write_test_result_json(dic=dic, file_path="test_result.json")
        test_rel = read_test_result_json(file_path='test_result.json', dic_key="Result")
        print(test_rel)
        self.assertEqual(test_rel, "abc")


if __name__ == '__main__':
    unittest.main()
