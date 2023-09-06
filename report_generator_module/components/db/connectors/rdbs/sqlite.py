from report_generator_module.components.db.connectors.rdbs.base import BaseRDBConnector


class SQLiteConnector(BaseRDBConnector):

    @property
    def provider_name(self):
        return 'sqlite3'

    def fetch_all(self, res):
        return res.fetchall()

    def get_column_names(self, cursor):
        return [description[0] for description in cursor.description]
