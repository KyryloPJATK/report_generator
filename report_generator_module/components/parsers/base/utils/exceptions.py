from report_generator_module.components.grammar.base_grammar import BaseGrammar


class ParserException(Exception):
    """ Basic parser exception """

    def __init__(self, line_idx: int, message: str):
        super().__init__(f'Line {line_idx}: "{message}"')


class UnsetVariableException(ParserException):
    """ Exception called when there is a request to the variable that is unset """

    def __init__(self, line_idx: int, missing_variable: str):
        self.missing_variable = missing_variable
        super().__init__(line_idx, f'Variable "{self.missing_variable}" is missing')


class PatternValidationException(ParserException):
    """ Basic exception occurred during pattern validation """

    def __init__(self, line_idx: int, pattern: BaseGrammar, reason: str = 'Unknown error'):
        self.line_idx = line_idx
        self.pattern = pattern
        super().__init__(line_idx=line_idx, message=f'Pattern "{self.pattern.value}" validation failed. '
                                                    f'Reason: "{reason}"')


class QueryFailedException(ParserException):
    """ Exception occurred when SQL statement execution fails """

    def __init__(self, line_idx, sql_string, issue):
        self.sql_string = sql_string
        self.issue = issue
        super().__init__(line_idx=line_idx, message=f'Execution of SQL statement "{self.sql_string}" '
                                                    f'failed due to exception: "{self.issue}"')


class UnknownFunctionException(ParserException):
    """ Exception occurred when SQL statement execution fails """

    def __init__(self, line_idx, function_name):
        super().__init__(line_idx=line_idx, message=f'Unresolved function name: "{function_name}"')


class UnresolvedParametersException(Exception):
    """ Basic parser exception """

    def __init__(self, line_idx: int, failed_params: str):
        super().__init__({'line_idx': line_idx, 'failed_params': failed_params})
