import unittest
# command below will run this test
# python3 -m unittest discover -s tests

# command below will run all
# python3 -m nose

# command pytest
# python3 -m pytest

from sample.my_sum import sum

class TestSumList(unittest.TestCase):
    def test_list_int(self):
        """
        Test that it can sum a list of integers
        """
        data = [1, 2, 3, 4]
        result = sum(data)
        # fail
        self.assertEqual(result, 6)


class TestSumTuple(unittest.TestCase):
    """
    Test that it can sum a tuple of integers
    """
    def test_sum(self):
        # pass
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

    def test_sum_tuple(self):
        # fail
        self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")

class TestSum(unittest.TestCase):
    """
    Test that basic sum
    """
    def test_sum(self):
        # pass
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")


if __name__ == '__main__':
    unittest.main()