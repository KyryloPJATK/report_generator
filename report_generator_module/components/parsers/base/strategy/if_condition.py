import logging
import re

from report_generator_module.components.parsers.base.utils.parsing_utils import get_real_value
from report_generator_module.utils.iterable_utils import replace
from report_generator_module.components.grammar.base_grammar import BaseGrammar
from report_generator_module.components.parsers.base.strategy.scopable import ScopeParsingStrategy
from report_generator_module.components.parsers.base.utils.exceptions import UnsetVariableException
from pyparsing import OpAssoc, CaselessKeyword, Word, alphas, infix_notation, one_of


logger = logging.getLogger(__name__)


class BoolOperand:
    def __init__(self, t):
        self.label = t[0]
        self.value = eval(t[0])

    def __bool__(self):
        return self.value

    def __str__(self):
        return self.label

    __repr__ = __str__
    __nonzero__ = __bool__


class BoolBinOp:

    representing_symbol = ''
    evaluation_operator = None

    def __init__(self, t):
        self.args = t[0][0::2]

    def __str__(self):
        sep = " %s " % self.representing_symbol
        return "(" + sep.join(map(str, self.args)) + ")"

    def __bool__(self):
        return self.evaluation_operator(bool(a) for a in self.args)

    __nonzero__ = __bool__
    __repr__ = __str__


class BoolAnd(BoolBinOp):
    representing_symbol = '&'
    evaluation_operator = all


class BoolOr(BoolBinOp):
    representing_symbol = '|'
    evaluation_operator = any


class BoolNot:
    def __init__(self, t):
        self.arg = t[0][1]

    def __bool__(self):
        v = bool(self.arg)
        return not v

    def __str__(self):
        return "~" + str(self.arg)

    __repr__ = __str__
    __nonzero__ = __bool__


class IfConditionParser(ScopeParsingStrategy):

    TRUE = CaselessKeyword("True")
    FALSE = CaselessKeyword("False")
    boolOperand = TRUE | FALSE | Word(alphas)
    boolOperand.setParseAction(BoolOperand)

    # define expression, based on expression operand and
    # list of operations in precedence order
    bool_expression_parser = infix_notation(boolOperand,
                             [
                                 (one_of(("not",), caseless=True), 1, OpAssoc.RIGHT, BoolNot),
                                 (one_of(("and",), caseless=True), 2, OpAssoc.LEFT, BoolAnd),
                                 (one_of(("or",), caseless=True), 2, OpAssoc.LEFT, BoolOr),
                             ])

    def __init__(self, pattern: BaseGrammar, context: dict):
        super().__init__(pattern, context)
        self.operand_mapping = {
            '==': lambda x, y: get_real_value(self.context, x) == get_real_value(self.context, y),
            '!=': lambda x, y: get_real_value(self.context, x) != get_real_value(self.context, y),
            '<>': lambda x, y: get_real_value(self.context, x) != get_real_value(self.context, y),
            '>=': lambda x, y: float(get_real_value(self.context, x)) >= float(get_real_value(self.context, y)),
            '>': lambda x, y: float(get_real_value(self.context, x)) > float(get_real_value(self.context, y)),
            '<=': lambda x, y: float(get_real_value(self.context, x)) <= float(get_real_value(self.context, y)),
            '<': lambda x, y: float(get_real_value(self.context, x)) < float(get_real_value(self.context, y)),
        }

    def pre_parse(self, line: str) -> None:
        self.context.setdefault('current_scope_idx', 0)
        if self.current_scope_idx < 0:
            self.raise_exception('Syntax error: condition scope mismatch')
        elif self.pattern in (BaseGrammar.ELIF_CONDITION, BaseGrammar.ELSE,) and self.current_scope_idx == 0:
            self.raise_exception('Failed to execute ELIF condition outside condition scope')
        elif self.pattern == BaseGrammar.IF_CONDITION:
            self.current_scope_idx += 1
        self.context.setdefault('condition_state', {}).setdefault(self.current_scope_idx, {}).setdefault('condition_met', False)
        self.context.pop('await_state', None)

    def fetch_value(self, token: str):
        token = token.strip()
        if token.isdigit() or any(token.startswith(_chr) for _chr in ("'", '"')):
            return eval(token)
        else:
            value = self.context['variable_mapping'].get(token)
            if value is None:
                raise UnsetVariableException(line_idx=self.context.get('source_line_idx', -1), missing_variable=token)
            return value

    def evaluate_predicate(self, predicate: str) -> bool:
        try:
            if predicate.upper() == 'TRUE':
                return True
            elif predicate.upper() == 'FALSE':
                return False
            for k, func in self.operand_mapping.items():
                if k in predicate:
                    return func(*predicate.split(k,))
            return eval(predicate)
        except UnsetVariableException as un_ex:
            raise un_ex
        except Exception as ex:
            logger.error(ex)
            self.raise_exception('Malformed logical condition')

    def evaluate_line(self, line: str):
        while '(' in line:
            start_idx = line.index('(')
            last_idx = line.rindex(')')
            if last_idx < 0:
                self.raise_exception('Missing closing parenthesis in expression')
            evaluation_result = self.evaluate_line(line[start_idx+1:last_idx])
            line = replace(line,
                           evaluation_result,
                           start_idx,
                           last_idx)
        predicates = re.split(f" AND | OR ", line)
        replace_mapping = {}
        for predicate in predicates:
            predicate = predicate \
                .replace('NOT', '').strip()
            replace_mapping[predicate] = self.evaluate_predicate(predicate)
        for predicate, outcome in replace_mapping.items():
            line = re.sub(r'{predicate}'.format(predicate=predicate), str(outcome).upper(), line)
        return str(bool(self.bool_expression_parser.parse_string(line)[0])).upper()

    def parse(self, line: str) -> str:
        if self.pattern == BaseGrammar.ENDIF:
            self.context['condition_state'].pop(self.current_scope_idx, None)
            self.current_scope_idx -= 1
        elif self.pattern in (BaseGrammar.IF_CONDITION, BaseGrammar.ELIF_CONDITION, BaseGrammar.ELSE,):
            # Means that one of the condition is already met
            if self.context['condition_state'][self.current_scope_idx]['condition_met']:
                self.context['skip_copy'] = True
                self.context['await_state'] = {
                    'increment_if_nested': [BaseGrammar.IF_CONDITION.name],
                    'commands': [BaseGrammar.ENDIF.name],
                    'decrement_if_nested': [BaseGrammar.ENDIF.name],
                    'nested_buffer': 0
                }
            else:
                if self.pattern == BaseGrammar.ELSE:
                    condition_met = True
                else:
                    line = self.evaluate_line(line.replace('ELIF', '').replace('IF', ''))
                    logger.info(f'line after evaluation = {line}')
                    condition_met = bool(self.bool_expression_parser.parse_string(line)[0])
                self.context['condition_state'][self.current_scope_idx]['condition_met'] = condition_met
                if not condition_met:
                    self.context['skip_copy'] = True
                    if self.pattern == BaseGrammar.ELSE:
                        self.context['await_state'] = {
                            'increment_if_nested': [BaseGrammar.IF_CONDITION.name],
                            'commands': [BaseGrammar.ENDIF.name],
                            'decrement_if_nested': [BaseGrammar.ENDIF.name],
                            'nested_buffer': 0
                        }
                    else:
                        self.context['await_state'] = {
                            'increment_if_nested': [BaseGrammar.IF_CONDITION.name],
                            'commands': [BaseGrammar.ENDIF.name, BaseGrammar.ELIF_CONDITION.name, BaseGrammar.ELSE.name],
                            'decrement_if_nested': [BaseGrammar.ENDIF.name],
                            'nested_buffer': 0
                        }
