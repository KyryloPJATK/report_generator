import logging
from typing import Type, Dict

from report_generator_module.components.grammar.base_grammar import BaseGrammar
from tests.grammar_tests.base import TestGrammar

logger = logging.getLogger(__name__)


class GrammarTestFactory:

    # Add specific test handlers here
    LEXEME_TO_HANDLER: Dict[BaseGrammar, Type[TestGrammar]] = {}

    def create(self, lexeme: BaseGrammar):
        test_instance = self.LEXEME_TO_HANDLER.get(lexeme, TestGrammar)

        test_instance.run()

