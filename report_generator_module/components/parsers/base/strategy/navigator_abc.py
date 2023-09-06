import logging
from abc import ABC
from typing import Dict, Type, Union

from report_generator_module.components.grammar.base_grammar import BaseGrammar
from report_generator_module.components.parsers.base.strategy.assignment import AssignmentParser
from report_generator_module.components.parsers.base.strategy.for_loop import ForLoopParser
from report_generator_module.components.parsers.base.strategy.function_call import FunctionParser
from report_generator_module.components.parsers.base.strategy.if_condition import IfConditionParser
from report_generator_module.components.parsers.base.strategy.strategy_abc import BaseParsingStrategy


logger = logging.getLogger(__name__)


class ParsingStrategyNavigator(ABC):

    # Mapping of Grammar Pattern to Strategy
    # TODO: add common pattern strategy here
    lexeme_to_context: Dict[BaseGrammar, Type[BaseParsingStrategy]] = {
        BaseGrammar.IF_CONDITION.name: IfConditionParser,
        BaseGrammar.ELIF_CONDITION.name: IfConditionParser,
        BaseGrammar.ELSE.name: IfConditionParser,
        BaseGrammar.ENDIF.name: IfConditionParser,
        BaseGrammar.FUNCTION.name: FunctionParser,
        BaseGrammar.FOR_LOOP.name: ForLoopParser,
        BaseGrammar.ENDFOR.name: ForLoopParser,
        BaseGrammar.ASSIGNMENT.name: AssignmentParser,
    }

    def __init__(self):
        self.strategy: BaseParsingStrategy = None

    def init_strategy(self, source_pattern: BaseGrammar, context: dict) -> Union[BaseParsingStrategy, None]:
        """ Initialise strategy based on the provided pattern"""
        if source_pattern:
            matching_strategy = self.lexeme_to_context.get(source_pattern.name)
            if matching_strategy:
                self.strategy = matching_strategy(pattern=source_pattern, context=context)

    def execute(self, line: str) -> dict:
        """ Executes current strategy if initialised """
        if self.strategy:
            return self.strategy.execute(line)
        else:
            logger.error('No strategy initialised')
