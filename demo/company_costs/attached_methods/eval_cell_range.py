from string import ascii_uppercase

from report_generator_module.components.parsers.xlsx.parser import ExcelParser
from report_generator_module.utils.common_utils import extract_number_from_string


def column_name_to_index(column_name):
    """Convert Excel-style column name to zero-based column index."""
    index = 0
    for char in column_name:
        index = index * 26 + (ord(char.upper()) - ord('A') + 1)
    return index


def process(context: dict, cell_range: str):
    from_cell, to_cell = cell_range.split(":")
    from_cell = ExcelParser.replace_formula_row_idx(context=context, formula_str=from_cell)
    to_cell = ExcelParser.replace_formula_row_idx(context=context, formula_str=to_cell)

    min_row = extract_number_from_string(s=from_cell)
    max_row = extract_number_from_string(s=to_cell)

    return {"min_col": column_name_to_index(column_name=from_cell.split(min_row)[0]),
            "min_row": int(min_row),
            "max_col": column_name_to_index(column_name=to_cell.split(max_row)[0]),
            "max_row": int(max_row)}
