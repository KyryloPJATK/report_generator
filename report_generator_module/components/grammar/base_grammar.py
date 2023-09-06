from enum import Enum


class BaseGrammar(Enum):
    """ Enum of basic grammar regexes to apply while interpreting incoming instructions """
    RESERVED_KEYWORDS = r'\b(AND|OR|NOT|IF|ELIF|ENDIF|FOR|ENDFOR|IN|TRUE|FALSE)\b'
    ANY_WHITESPACES = r'\s*'
    AT_LEAST_ONE_WHITESPACE = r'\s+'
    VARIABLE_NAME = r'[a-zA-Z_$][a-zA-Z_$0-9]*'
    VARIABLE_EXPRESSION = r'~\{.*?\}'
    FUNCTION = r'({VARIABLE_NAME}(?=\().+\))'.format(VARIABLE_NAME=VARIABLE_NAME)
    # ANY_ALPHANUM = r"^.*[a-zA-Z0-9]+.*$"
    ANY_LOGICAL_COMPARISON = '>|>=|==|<|<=|!=|<>'
    VALID_INTEGER = r'[+-]?([0]|[1-9]+[0-9]*)'
    VALID_FLOAT = r'{VALID_INTEGER}([.][0-9]+)?'.format(VALID_INTEGER=VALID_INTEGER)
    VALID_STRING = r'\".*\"'
    VALID_VALUE = r'{VALID_FLOAT}|{VALID_STRING}|{VARIABLE_NAME}'.format(VALID_FLOAT=VALID_FLOAT, VALID_STRING=VALID_STRING, VARIABLE_NAME=VARIABLE_NAME)
    ARRAY = r'\((({VALID_VALUE})(,{VALID_VALUE})*)?\)'.format(VALID_VALUE=VALID_VALUE)
    ASSIGNMENT = r'({VARIABLE_NAME}){ANY_WHITESPACES}={ANY_WHITESPACES}({VALID_VALUE}|{ARRAY})'.format(VARIABLE_NAME=VARIABLE_NAME, ANY_WHITESPACES=ANY_WHITESPACES, VALID_VALUE=VALID_VALUE, ARRAY=ARRAY)
    # TODO: uncomment if needed
    # COMPARISON = r'(NOT{AT_LEAST_ONE_WHITESPACE})?{VALID_VALUE}{ANY_WHITESPACES}[{ANY_LOGICAL_COMPARISON}{ANY_WHITESPACES}(NOT{AT_LEAST_ONE_WHITESPACE})?{VALID_VALUE}]?'.format(AT_LEAST_ONE_WHITESPACE=AT_LEAST_ONE_WHITESPACE,
    #                                                                                                                                                                              ANY_WHITESPACES=ANY_WHITESPACES,
    #                                                                                                                                                                              VALID_VALUE=VALID_VALUE,
    #                                                                                                                                                                              ANY_LOGICAL_COMPARISON=ANY_LOGICAL_COMPARISON)
    # LOGICAL_CONDITION = r"(?!.*(?<!\S)(?:{RESERVED_KEYWORDS})\s*(?:AND|OR)(?!\S))\s*({COMPARISON}))\s*((AND|OR)\s+({COMPARISON}))\s*)*".format(RESERVED_KEYWORDS=RESERVED_KEYWORDS,
    #                                                                                                                                            COMPARISON=COMPARISON)
    IF_CONDITION = r'IF{AT_LEAST_ONE_WHITESPACE}(.*)'.format(AT_LEAST_ONE_WHITESPACE=AT_LEAST_ONE_WHITESPACE)
    ELIF_CONDITION = r'ELIF{AT_LEAST_ONE_WHITESPACE}(.*)'.format(AT_LEAST_ONE_WHITESPACE=AT_LEAST_ONE_WHITESPACE)
    ELSE = r'\bELSE\b'
    ENDIF = r'\bENDIF\b'
    FOR_LOOP = r'FOR{AT_LEAST_ONE_WHITESPACE}{VARIABLE_NAME}{AT_LEAST_ONE_WHITESPACE}IN{AT_LEAST_ONE_WHITESPACE}({ARRAY}|{VALID_VALUE})'.format(VARIABLE_NAME=VARIABLE_NAME,
                                                                                                                                                ARRAY=ARRAY,
                                                                                                                                                VALID_VALUE=VALID_VALUE,
                                                                                                                                                AT_LEAST_ONE_WHITESPACE=AT_LEAST_ONE_WHITESPACE)
    ENDFOR = r'\bENDFOR\b'
