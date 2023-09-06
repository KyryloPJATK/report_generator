from report_generator_module.components.db.connectors.rdbs.base import BaseRDBConnector


class MySQLConnector(BaseRDBConnector):

    def get_column_names(self, cursor):
        return cursor.column_names

    @property
    def provider_name(self):
        return 'mysql.connector'

    def fetch_all(self, res):
        return res.fetch_all()
