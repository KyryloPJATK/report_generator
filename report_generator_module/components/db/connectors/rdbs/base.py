import importlib
from abc import abstractmethod

from munch import DefaultMunch

from report_generator_module.components.db.connectors.base import DatabaseConnector
from report_generator_module.components.parsers.base.utils.exceptions import QueryFailedException


class BaseRDBConnector(DatabaseConnector):

    def __init__(self, connection_creds: dict):
        self.connection_creds = connection_creds
        self._connection = None

    @property
    def provider_module(self):
        return importlib.import_module(self.provider_name)

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    def connect(self):
        self._connection = getattr(self.provider_module, 'connect')(**self.connection_creds)

    def close(self):
        if self._connection:
            self._connection.close()
        self._connection = None

    @abstractmethod
    def fetch_all(self, res):
        pass

    @abstractmethod
    def get_column_names(self, cursor):
        pass

    def get_result(self, cursor, res_obj):
        data = self.fetch_all(res=res_obj)
        column_names = self.get_column_names(cursor)
        if data:
            return [DefaultMunch.fromDict(dict(zip(column_names, item))) for item in data]

    def execute_sql(self, query: str, return_data: bool = False, context: dict = None):
        if not context:
            context = {}
        curr = self._connection.cursor()
        try:
            res = curr.execute(query)
            if return_data:
                res = self.get_result(cursor=curr, res_obj=res)
        except Exception as ex:
            raise QueryFailedException(line_idx=context.get('source_line_idx', -1),
                                       sql_string=query,
                                       issue=str(ex))
        finally:
            curr.close()
        return res
