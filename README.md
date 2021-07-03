source https://realpython.com/python-testing/

# nose2

To get started with nose2, install nose2 from PyPI and execute it on the command line. 
nose2 will try to discover all test scripts named test*.py and test cases inheriting from unittest.TestCase in your current directory:

https://nose2.readthedocs.io/

``` bash
# command to run all pytest and unittest
python3 -m nose2
```

# pytest

pytest supports execution of unittest test cases. The real advantage of pytest comes by writing pytest test cases. pytest test cases are a series of functions in a Python file starting with the name test_.

https://docs.pytest.org/en/latest/

pytest has some other great features:

* Support for the built-in assert statement instead of using special self.assert*() methods
* Support for filtering for test cases
* Ability to rerun from the last failing test
* An ecosystem of hundreds of plugins to extend the functionality

``` bash
python3 -m pytest tests/test_sum_pytest.py
```

# unittest

```bash
python3 -m unittest tests/test_my_sum/test.py
# verbose
python3 -m unittest -v tests/test_my_sum/test.py
```

# Note: What if your application is a single script?

You can import any attributes of the script, such as classes, functions, and variables by using the built-in __import__() function. Instead of from my_sum import sum, you can write the following:

target = __import__("my_sum.py")
sum = target.sum

The benefit of using __import__() is that you don’t have to turn your project folder into a package, and you can specify the file name. This is also useful if your filename collides with any standard library packages. For example, math.py would collide with the math module.

# Assert

| Method                  | Equivalent to    |
| ----------------------- | ---------------- |
| .assertEqual(a, b)      | a == b           |
| .assertTrue(x)          | bool(x) is True  |
| .assertFalse(x)         | bool(x) is False |
| .assertIs(a, b)         | a is b           |
| .assertIsNone(x)        | x is None        |
| .assertIn(a, b)         | a in b           |
| .assertIsInstance(a, b) | isinstance(a, b) |


Instead of providing the name of a module containing tests, you can request an auto-discovery using the following:

```bash
python3 -m unittest discover
```

Once you have multiple test files, as long as you follow the test*.py naming pattern, you can provide the name of the directory instead by using the -s flag and the name of the directory:

```bash
python3 -m unittest discover -s tests
```

Lastly, if your source code is not in the directory root and contained in a subdirectory, for example in a folder called src/, you can tell unittest where to execute the tests so that it can import the modules correctly with the -t flag:

```bash
python3 -m unittest discover -s tests -t src
```