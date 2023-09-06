import os
import logging
import re

from abc import ABC, abstractmethod
from typing import List, Union

from report_generator_module.components.grammar.base_grammar import BaseGrammar
from report_generator_module.components.parsers.base.strategy.navigator_abc import ParsingStrategyNavigator
from report_generator_module.components.parsers.base.utils.exceptions import ParserException
from report_generator_module.config import Configuration

logger = logging.getLogger(__name__)


class BaseParser(ABC):

    # Ordered patterns to be checked
    __PATTERN_VALIDATION_ORDER = (BaseGrammar.FOR_LOOP,
                                  BaseGrammar.ENDFOR,
                                  BaseGrammar.IF_CONDITION,
                                  BaseGrammar.ELIF_CONDITION,
                                  BaseGrammar.ELSE,
                                  BaseGrammar.ENDIF,
                                  BaseGrammar.ASSIGNMENT,
                                  BaseGrammar.FUNCTION)

    def __init__(self, config: Configuration):
        self._strategy = None
        self._script_lines = None
        self.config = config
        self.lexeme_leading_char = self.config.get('lexeme_leading_char', '::')
        self.source_path = os.path.expanduser(self.config.get('source_path'))
        self.file_type = self.source_path.split('.')[-1]
        self._script_lines = None

    @abstractmethod
    def init_strategy_navigator(self) -> ParsingStrategyNavigator:
        pass

    @property
    def strategy_navigator(self) -> ParsingStrategyNavigator:
        """ Returns strategy controller instance for given parser instance """
        if not self._strategy:
            self._strategy = self.init_strategy_navigator()
        return self._strategy

    @abstractmethod
    def init_script_lines(self) -> List[str]:
        pass

    @property
    def script_lines(self) -> List[str]:
        """ Returns list of script lines in order based on source path """
        if not self._script_lines:
            self._script_lines = self.init_script_lines()
        return self._script_lines

    @classmethod
    def get_matching_expression_pattern(cls, line: str) -> Union[BaseGrammar, None]:
        """
            Gets first matching expression based on provided line

            :param line: line string to check
            :returns Matched pattern or None if not found
        """
        for pattern in cls.__PATTERN_VALIDATION_ORDER:
            if bool(re.match(pattern.value, line)):
                return pattern

    @staticmethod
    def should_proceed(context: dict, matching_pattern: BaseGrammar):
        """
            Checks if context is in the state of awaiting on particular pattern
            E.g. IF condition failed -> waiting on ELIF or ENDIF
        """
        await_state = context.get('await_state')
        if await_state:
            if matching_pattern.name in await_state.get('increment_if_nested', []):
                await_state['nested_buffer'] += 1
            elif matching_pattern.name in await_state['commands']:
                if await_state['nested_buffer'] == 0:
                    return True
                elif matching_pattern.name in await_state.get('decrement_if_nested', []):
                    await_state['nested_buffer'] -= 1
            return False
        else:
            return True

    @abstractmethod
    def post_lexeme_parse(self, context: dict):
        pass

    def parse(self, context: dict = None) -> Union[ParserException, None]:
        """
            Parses logic stored in the source file and outputs results into the destination path

            :param context: parse context
        """
        destination_path = context['destination_path']
        logger.info(f'Initiating parsing from {self.source_path} to {destination_path}')
        # Joins global context with
        if not context:
            context = {}
        context = {**{'config': self.config,
                      'source_line_idx': 0,   # line index for the source template
                      'dest_line_idx': 0,     # line index for the destination file
                      'destination_path': destination_path,
                      'variable_mapping': {},
                      'row_idx_mapping': {},
                      'failed_params': {}},
                   **context}
        while True:
            try:
                context['source_line_idx'] = context.pop('force_line_idx', context['source_line_idx']+1)
                if context['source_line_idx'] > len(self.script_lines):
                    break
                line = self.script_lines[context['source_line_idx']-1]
                if isinstance(line, str) and line.startswith(self.lexeme_leading_char):
                    dropline_str = f'{self.lexeme_leading_char}DROPLINE'
                    if line.endswith(dropline_str):
                        context['skip_copy'] = True
                        line = line.rsplit(dropline_str, 1)[0]
                    line = line.upper().lstrip(self.lexeme_leading_char)
                    matching_pattern = self.get_matching_expression_pattern(line)
                    should_process = self.should_proceed(context, matching_pattern)
                    if should_process:
                        logger.info(f'Received matching pattern on line #{context["source_line_idx"]}')
                        self.strategy_navigator.init_strategy(source_pattern=matching_pattern, context=context)
                        context = self.strategy_navigator.execute(line=line) or context
                    else:
                        logger.info(f'Waiting on one of patterns: {context.get("await_commands")}')
                        continue
                if not context.pop('skip_copy', False):
                    self.post_lexeme_parse(context=context)
            except ParserException as ex:
                logger.error(f'Parsing exception occurred on iterating {self.source_path} - {ex}')
                return ex
        context['wb_out'].save(context['destination_path'])
        logger.info(f'Parsing from "{self.source_path}" to "{destination_path}" completed successfully')
