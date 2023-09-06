from report_generator_module.components.parsers.xlsx.parser import ExcelParser


def process(context: dict, cell: str):
    return ExcelParser.replace_formula_row_idx(context=context, formula_str=cell)
