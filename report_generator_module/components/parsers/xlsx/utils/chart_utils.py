from typing import Optional

import pandas as pd

from pandas.io.excel._xlsxwriter import XlsxWriter

from report_generator_module.components.parsers.xlsx.enums import ChartTypes


def inject_chart(writer: XlsxWriter, sheet_name: str, cell: str, df: pd.Dataframe, chart_type: ChartTypes,
                 chart_subtype: Optional[str] = None, series_options: dict = None):
    """
        Injects char into Excel according to provided params

        :param writer: Xlsx Writer instance
        :param sheet_name: name of the Excel sheet to consider
        :param cell: name of the cell to save the result to
        :param df: dataframe with the input data
        :param chart_type: type of the chart to display from ChartTypes
        :param chart_subtype: chart subtype to display (if applicable)
        :param series_options: options of the series
    """
    df.to_excel(writer, sheet_name=sheet_name)

    # Access the XlsxWriter workbook and worksheet objects from the dataframe.
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # Create a chart object.
    chat_options = {'type': chart_type.value}
    if chart_subtype:
        chat_options['subtype'] = chart_subtype
    chart = workbook.add_chart(chat_options)

    # TODO: fetch chart properties based on its type
    if not series_options:
        series_options = {}
    chart.add_series(series_options)
    worksheet.insert_chart(cell, chart)
    return writer

