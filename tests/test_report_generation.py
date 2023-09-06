import unittest

from report_generator_module.controller import ReportGenerator


class TestReportGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.generator = ReportGenerator()

    def test_excel_parser(self):
        self.generator.run(source_path='repgen.xlsx',
                           destination_path='repgen.xlsx',
                           context={'destination_sheet_name': 'Sheet_Processed',
                                    'source_context': {'sheet_name': 'Template'},
                                    'variable_mapping': {'TEST_STR': '123',
                                                         'TEST_ENUM': 1,
                                                         'TEST_QUERY': 'John'}})
