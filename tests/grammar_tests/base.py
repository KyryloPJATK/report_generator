import re
import unittest
from abc import abstractmethod


class TestGrammar(unittest.TestCase):

    lexeme = None  # regex string to test
    valid_cases = []  # list of valid cases
    invalid_cases = []  # list of invalid cases

    @classmethod
    def setUpClass(cls) -> None:
        cls.re_compiled = re.compile(cls.lexeme, re.IGNORECASE)

    def test_01_validate_regex(self):
        """ Asserts that for selected number of test cases the result is predictable """
        for case in self.valid_cases:
            self.assertTrue(bool(re.match(self.re_compiled, case)), msg=f'{case} should be valid!')
        for case in self.invalid_cases:
            self.assertFalse(bool(re.match(self.re_compiled, case)), msg=f'{case} should be invalid!')

    @abstractmethod
    def test_02_validate_parser(self):
        """ Asserts that regex parser returns predictable tokens from valid expressions """
        pass
