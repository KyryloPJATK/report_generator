import re
from pprint import pprint

from report_generator_module.components.grammar.base_grammar import BaseGrammar


def get_real_value(context: dict, raw_data: str):
    """
        Gets factual value from provided string based on the current context and parsed result
        :param context: Report Generator Context object
        :param raw_data: incoming expression to parse
    """
    if not raw_data:
        return
    result = raw_data.strip()
    primitive_to_type = {
        BaseGrammar.VALID_INTEGER.name: int,
        BaseGrammar.VALID_STRING.name: str,
        BaseGrammar.VALID_FLOAT.name: float
    }
    patterns_to_eval = [BaseGrammar.ARRAY,
                        BaseGrammar.FUNCTION,
                        BaseGrammar.VALID_STRING,
                        BaseGrammar.VALID_INTEGER,
                        BaseGrammar.VALID_FLOAT,
                        BaseGrammar.VARIABLE_NAME]
    try:
        if re.match(BaseGrammar.VARIABLE_EXPRESSION.value, str(raw_data)):
            result = result[2:-1]
            patterns_to_eval = [BaseGrammar.VARIABLE_NAME]
    except TypeError:
        print(f'Received {result} | {type(result)}')
    for pattern in patterns_to_eval:
        try:
            if re.match(pattern.value, str(result)):
                if pattern.name == BaseGrammar.ARRAY.name:
                    result = eval(result.replace('(', '[').replace(')', ']'))
                elif pattern.name == BaseGrammar.FUNCTION.name:
                    from report_generator_module.components.parsers.base.strategy.function_call import FunctionParser
                    func_parsing_strategy = FunctionParser(context=context, pattern=BaseGrammar.FUNCTION)
                    result = func_parsing_strategy.parse(result)
                elif pattern.name == BaseGrammar.VALID_STRING.name:
                    for token in ["'", '"']:
                        if result.startswith(token):
                            result = str(result.strip(token))
                elif pattern.name in (BaseGrammar.VALID_INTEGER.name,
                                      BaseGrammar.VALID_FLOAT.name,):
                    result = primitive_to_type[pattern.name](result)
                elif pattern.name == BaseGrammar.VARIABLE_NAME.name:
                    attributes_struct = result.split('.')
                    if len(attributes_struct) == 2:
                        target_object = context['variable_mapping'].get(attributes_struct[0].strip().upper())
                        target_object_attr = attributes_struct[1].strip()
                        # TODO: always set processing objects attributes to either lower- or uppercase
                        result = getattr(target_object, target_object_attr.lower()) or \
                                 getattr(target_object, target_object_attr.upper())
                    else:
                        result = context['variable_mapping'].get(result, result)
                return result
        except TypeError:
            pprint(f'Received raw_data={raw_data} | type={type(raw_data)}')
    return result or raw_data
