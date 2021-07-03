import pytest
from sample.my_sum import sum
# command below will run all
# python3 -m nose

# command to run pytest
# pytest


def test_sum():
    # pass
    assert sum([1, 2, 3]) == 6, "Should be 6"

def test_sum_tuple():
    # fail
    assert sum((1, 2, 2)) == 6, "Should be 6"