from report_generator_module.components.grammar.base_grammar import BaseGrammar
from tests.grammar_tests.base import TestGrammar


class TestLoops(TestGrammar):

    lexeme = BaseGrammar.FOR_LOOP

    def test_02_validate_parser(self):
        pass

