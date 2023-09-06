from report_generator_module.components.parsers.base.strategy.strategy_abc import BaseParsingStrategy
from report_generator_module.components.parsers.base.utils.parsing_utils import get_real_value


class AssignmentParser(BaseParsingStrategy):

    def parse(self, line: str) -> None:
        var_name, expression = line.split('=', maxsplit=1)
        var_name = var_name.strip()
        expression = expression.strip()
        self.context["variable_mapping"][var_name] = get_real_value(context=self.context,
                                                                    raw_data=expression)
