import re

from report_generator_module.components.grammar.base_grammar import BaseGrammar
from report_generator_module.components.parsers.base.utils.parsing_utils import get_real_value
from report_generator_module.components.db.connectors.rdbs.mysql import MySQLConnector
from report_generator_module.components.db.connectors.rdbs.postgres import PostgresConnector
from report_generator_module.components.db.connectors.rdbs.sqlite import SQLiteConnector


class DatabaseFactory:

    __connectors = {}
    __dialect_connectors = {
        'mysql': MySQLConnector,
        'sqlite': SQLiteConnector,
        'postgres': PostgresConnector
    }

    @classmethod
    def get_connection_for_alias(cls, context: dict,  alias: str):
        if not cls.__connectors.get(alias):
            connection_config = context['config'].get_db_properties_by_alias(alias)
            if connection_config:
                db_type = connection_config.pop("type")
                cls.__connectors[alias] = cls.__dialect_connectors[db_type](connection_creds=connection_config)
            else:
                raise AttributeError(f"alias={alias} is was not found")
        return cls.__connectors[alias]

    @classmethod
    def execute_sql(cls, context, query: str, alias=None, limit: int = None):
        handler = cls.get_connection_for_alias(context=context, alias=alias)
        handler.connect()
        try:
            query = query.strip('"')
            parameter_matches = re.findall(BaseGrammar.VARIABLE_EXPRESSION.value, str(query))
            for match in parameter_matches:
                real_val = get_real_value(context, match)
                if real_val:
                    query = query.replace(match, str(real_val))
            execution_kwargs = {'query': query, 'context': context}
            if query.strip().upper().startswith('SELECT'):
                execution_kwargs['return_data'] = True
            execution_result = handler.execute_sql(**execution_kwargs)
        finally:
            handler.close()
        if limit and execution_result:
            if limit == 1:
                execution_result = execution_result[0]
            else:
                execution_result = execution_result[:limit]
        return execution_result
