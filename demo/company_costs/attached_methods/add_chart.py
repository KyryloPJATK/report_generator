from openpyxl.chart import PieChart, LineChart, BarChart, BubbleChart, ScatterChart, StockChart, Reference

from report_generator_module.components.parsers.base.utils.parsing_utils import get_real_value

chats_cache = {}


chart_type_to_cls = {
    "pie": PieChart,
    "line": LineChart,
    "bar": BarChart,
    "bubble": BubbleChart,
    "scatter": ScatterChart,
    "stock": StockChart,
}


def process(context: dict, dest_cell, chart_type: str, chart_title: str, source_labels, source_data):

    chart = chart_type_to_cls.get(chart_type.lower())()

    if not chart:
        raise AttributeError(f"Unresolved chart_type={chart_type}")

    dest_cell = get_real_value(context=context,
                               raw_data=dest_cell)
    # TODO: now it can only fetch already created table; make it work with raw source data
    # labels_data = get_real_value(context=context, raw_data=source_labels)
    # source_data = get_real_value(context=context, raw_data=source_values)

    data_copier = context['data_copier']

    labels = Reference(data_copier.ws_out, **source_labels)
    data = Reference(data_copier.ws_out, **source_data)
    chart.add_data(data=data, titles_from_data=False)
    chart.set_categories(labels=labels)
    chart.title = chart_title

    # Add the chart to the worksheet
    data_copier.ws_out.add_chart(chart, dest_cell)
