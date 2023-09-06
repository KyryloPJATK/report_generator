from abc import ABC, abstractmethod
from typing import Type

from report_generator_module.components.grammar.base_grammar import BaseGrammar
from report_generator_module.components.parsers.base.utils.exceptions import PatternValidationException


class BaseParsingStrategy(ABC):

    def __init__(self, pattern: BaseGrammar, context: dict):
        self.pattern = pattern
        self.context = context

    def raise_exception(self, msg: str, exception_class: Type[PatternValidationException] = PatternValidationException, **context):
        """ Raises any Exception inheriting PatternValidationException with prefilling some context-based arguments """
        raise exception_class(self.context.get('source_line_idx', -1), pattern=self.pattern, reason=msg)

    @abstractmethod
    def parse(self, line: str) -> None:
        """
            Executes logic based on the initialized context

            :param line: command string to execute
            :returns updated context
        """
        pass

    def pre_parse(self, line: str) -> None:
        """ Override this method to do any pre-parsing checks"""
        pass

    def post_parse(self, line: str) -> None:
        """ Override this method to do any post-parsing checks"""
        pass

    def execute(self, line: str) -> dict:
        """ Executes provided line and returns updated context """
        self.pre_parse(line=line)
        self.parse(line=line)
        self.post_parse(line=line)
        return self.context
