from typing import List, Union

from munch import DefaultMunch

from report_generator_module.components.parsers.base.utils.exceptions import UnresolvedParametersException
from report_generator_module.components.parsers.base.utils.parsing_utils import get_real_value

SUPPORTED_PARAM_TYPES = ["NUMBER", "STRING", "ENUM"]


def check_number_param(context: dict, param_value: str) -> str:
    """ Check if NUMBER parameter is a valid number """
    err_msg = None
    if not param_value:
        err_msg = f'Value is not defined'
    elif not str(param_value).isnumeric():
        err_msg = 'Non-numeric value provided'
    return err_msg


def check_str_param(context: dict, param_value: str) -> str:
    """ Check if STRING parameter is a valid string """
    err_msg = None
    if not param_value:
        err_msg = f'Value is not defined'
    elif not isinstance(param_value, str):
        err_msg = 'Type of parameter provided do not match type STRING'
    return err_msg


def check_enum_param(context: dict, param_value: str, supported_values: Union[List[str], str]) -> str:
    """ Check if ENUM parameter is a valid enum member """
    supported_values = get_real_value(context, supported_values)
    if isinstance(supported_values[0], DefaultMunch):
        supported_values = [getattr(supported_value, list(supported_value)[0]) for supported_value in supported_values]
    err_msg = None
    if not param_value:
        err_msg = f'Value is not defined, should be one of {supported_values}'
    elif param_value not in supported_values:
        err_msg = f'Value {param_value} is not of supported, should be one of {supported_values}'
    return err_msg


param_validators = {
    "NUMBER": check_number_param,
    "STRING": check_str_param,
    "ENUM": check_enum_param
}


def assert_param(context: dict, name: str, param_type: str, *args, **kwargs):
    """
        Asserts that requested parameter is provided in context
        :param context: Parser context
        :param name: Parameter name
        :param param_type: name denoting type of param provided, should be one of SUPPORTED_PARAM_TYPES
    """
    param_value = context['variable_mapping'].get(name)
    param_type = get_real_value(context, param_type).upper()
    if param_type not in list(param_validators):
        err_message = f'Type "{param_type}" was not resolved supported are - {SUPPORTED_PARAM_TYPES}.'
    else:
        err_message = param_validators[param_type](context,
                                                   param_value,
                                                   *args, **kwargs)
    if err_message:
        context['failed_params'][name] = {
            'type': param_type,
            'line_idx': context['source_line_idx'],
            'err_msg': err_message
        }


def ask_params(context: dict):
    """ Returns all the failed params if any """
    failed_params = context.get('failed_params', {})
    if failed_params:
        raise UnresolvedParametersException(line_idx=context['source_line_idx'], failed_params=failed_params)
