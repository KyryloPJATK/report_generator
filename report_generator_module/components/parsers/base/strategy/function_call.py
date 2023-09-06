import importlib
import re

from os import listdir
from os.path import isfile, join
from typing import Any, List

from report_generator_module.components.db.connectors.rdbs.factory import DatabaseFactory
from report_generator_module.components.parsers.base.utils.exceptions import UnknownFunctionException
from report_generator_module.components.parsers.base.utils.params_utils import assert_param, ask_params
from report_generator_module.components.parsers.base.utils.parsing_utils import get_real_value
from report_generator_module.components.parsers.base.strategy.strategy_abc import BaseParsingStrategy


ATTACHED_METHODS_PYTHON_PATH = "report_generator_module.components.parsers.base.attached_methods"
ATTACHED_METHODS_PATH = f'./{ATTACHED_METHODS_PYTHON_PATH.replace(".", "/")}'


def init_attached_methods() -> List[str]:
    return [f.split('.py')[0] for f in listdir(ATTACHED_METHODS_PATH)
            if isfile(join(ATTACHED_METHODS_PATH, f)) and f.endswith(".py")]


class FunctionParser(BaseParsingStrategy):
    __base_functions_mapping = {'exec_sql': DatabaseFactory.execute_sql,
                                'display': lambda x: print(x),
                                'range': lambda x: range(int(x)),
                                'param': assert_param,
                                'ask_params': ask_params}

    attached_methods = init_attached_methods()

    @staticmethod
    def split_by_comma(s):
        # Matches commas that are not within quotes
        pattern = re.compile(r',(?=(?:[^`{}]*`[^`{}]*`|{[^{}]*})*[^`{}]*$)')

        # Split the string using the pattern
        result = re.split(pattern, s)
        result = [i.strip('` ') for i in result]

        return result

    def parse_kwargs(self, function_args: str) -> dict:
        # TODO: make kwargs work
        kwargs_recognition_pattern = re.compile(r"(\w+)=(?:'(\w+)'|(\w+)|`(\w+)`),")
        kwargs = {}
        for arg in function_args:
            if re.match(kwargs_recognition_pattern, arg):
                match = kwargs_recognition_pattern.findall(function_args)[0]
                kwargs[match[0]] = get_real_value(self.context, match[1] or match[2] or match[3])
        return kwargs

    def _get_matching_callable(self, function_name: str):
        function_name = function_name.lower()
        if function_name in FunctionParser.attached_methods:
            matching_function = getattr(importlib.import_module(f"{ATTACHED_METHODS_PYTHON_PATH}.{function_name}"),
                                        "process")
        else:
            matching_function = self.__base_functions_mapping.get(function_name)
        return matching_function

    def parse(self, line: str) -> Any:
        line_lst = line.rsplit(')', maxsplit=1)[0].split('(', maxsplit=1)
        function_name = line_lst[0]
        matching_function = self._get_matching_callable(function_name=function_name)
        if matching_function:
            function_args = self.split_by_comma(line_lst[1])
            # Disabled kwargs due to parsing issue with inner functions. TODO: fix it
            # function_kwargs = self.parse_kwargs(function_args=function_args)
            # function_args = list(filter(lambda item: not any(i in item for i in function_kwargs), function_args))
            function_args = [get_real_value(self.context, x.strip()) for x in function_args]
            if function_args and function_args[0]:
                return matching_function(self.context, *function_args)
            else:
                return matching_function(self.context)
        else:
            raise UnknownFunctionException(self.context['source_line_idx'], function_name)
