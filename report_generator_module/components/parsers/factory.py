from report_generator_module.components.parsers.xlsx.parser import ExcelParser
from report_generator_module.config import Configuration


class ParsersFactory:

    source_to_parser = {
        'xlsx': ExcelParser,
        'xls': ExcelParser,
        'xlsm': ExcelParser
    }

    @classmethod
    def run(cls, source_type: str, context: dict, config: Configuration):
        matching_instance = cls.source_to_parser.get(source_type)(config=config)
        if matching_instance:
            matching_instance.parse(context=context)
