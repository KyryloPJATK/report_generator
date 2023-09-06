import logging
import re

from report_generator_module.components.grammar.base_grammar import BaseGrammar

TEST_SETS = {
    BaseGrammar.RESERVED_KEYWORDS: {
        'valid_cases': ['AND', 'OR', 'NOT', 'IF', 'ELIF', 'ENDIF', 'FOR', 'ENDFOR', 'IN', 'TRUE', 'FALSE'],
        'invalid_cases': ['NON RESERVED KEYWORD', '-AND', '+OR', 'ANDDD', 'OROR']
    },
    BaseGrammar.ANY_WHITESPACES: {
        'valid_cases': ['', ' ', '              '],
        'invalid_cases': []
    },
    BaseGrammar.AT_LEAST_ONE_WHITESPACE: {
        'valid_cases': [' ', '                '],
        'invalid_cases': ['']
    },
    BaseGrammar.VARIABLE_NAME: {
        'valid_cases': ['a', '_a', 'a1', 'B'],
        'invalid_cases': ['-a', '123', '*242']
    },
    BaseGrammar.FUNCTION: {
        'valid_cases': ['foo(a)', 'foo(a,b,c,d)', 'foo(123)', 'foo(abc)'],
        'invalid_cases': ['foo[a]']
    },
    BaseGrammar.ANY_LOGICAL_COMPARISON: {
        'valid_cases': ['<', '<=', '>', '>=', '==', '!='],
        'invalid_cases': ['!!', 'a']
    },
    BaseGrammar.VALID_NUMBER: {
        'valid_cases': ['1', '-1', '+1', '123', '0', '001'],
        'invalid_cases': ['a', '--1', '']
    },
    BaseGrammar.VALID_STRING: {
        'valid_cases': ['"hello"', '"world"'],
        'invalid_cases': ['123', '1', 'a', '()', 'foo(a)']
    },
    BaseGrammar.ARRAY: {
        'valid_cases': ['()', '(a)', '(1,2,3)',],
        'invalid_cases': ['[]', '{}', '[a)', '(a]', '(a;b;c)']
    },
    BaseGrammar.ASSIGNMENT: {
        'valid_cases': ['a=b', 'b= 1', 'c =(1,2,3)', 'd=foo(a)'],
        'invalid_cases': ['1=a', '-a=b', 'a>=b', 'a==b']
    },
    # BaseGrammar.COMPARISON: {
    #     'valid_cases': ['a<b', 'a<=b', 'ab>ac', 'ab>=ac', 'abc==abc', 'abb!=abc'],
    #     'invalid_cases': ['a!!b', 'ab']
    # },
    # BaseGrammar.LOGICAL_CONDITION: {
    #     'valid_cases': ['NOT A>B', 'A>B', 'A>1', 'NOT A>B AND B>C', 'B>C OR C<A'],
    #     'invalid_cases': ['A>B NOT', 'IF>ELSE', '']
    # },
    BaseGrammar.IF_CONDITION: {
        'valid_cases': ['IF A', 'IF NOT A', 'IF A>B AND B>C'],
        'invalid_cases': ['IFA>B', 'IF']
    },
    BaseGrammar.ELIF_CONDITION: {
        'valid_cases': ['ELIF A', 'ELIF NOT A', 'ELIF A>B AND B>C'],
        'invalid_cases': ['ELIFA', '_ELIF']
    },
    BaseGrammar.ENDIF: {
        'valid_cases': ['ENDIF'],
        'invalid_cases': ['ENDIFA', '_ENDIF']
    },
    BaseGrammar.FOR_LOOP: {
        'valid_cases': ['FOR I IN RANGE(3)', 'FOR I IN a', 'FOR I IN (1,2,3)', 'FOR I IN 1'],
        'invalid_cases': ['FOR I', 'FOR IN [1,2,3]']
    },
    BaseGrammar.ENDFOR: {
        'valid_cases': ['ENDFOR'],
        'invalid_cases': ['END FOR', 'END', 'FOR']
    },
}

logger = logging.getLogger(__name__)


if __name__ == '__main__':

    # TODO: move it to tests
    considered_lexemes = {}
    test_set = {k: v for k, v in TEST_SETS.items() if not considered_lexemes or considered_lexemes and k in considered_lexemes}
    for lexeme, cases in test_set.items():
        lexeme_value = lexeme.value
        lexeme_name = lexeme.name
        try:
            re_compiled = re.compile(lexeme_value, re.IGNORECASE)
            for case in cases['valid_cases']:
                try:
                    assert bool(re.match(re_compiled, case))
                except AssertionError as ex:
                    logger.error(f'{lexeme_name} | should be valid | {case}')
            for case in cases['invalid_cases']:
                try:
                    assert not bool(re.match(re_compiled, case))
                except AssertionError as ex:
                    logger.error(f'{lexeme_name} | should be invalid | {case}')
        except re.error as err:
            logger.error(f'Failed to compile regex={lexeme.value}: {err}')
