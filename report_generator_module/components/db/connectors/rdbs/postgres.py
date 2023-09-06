from report_generator_module.components.db.connectors.rdbs.base import BaseRDBConnector


class PostgresConnector(BaseRDBConnector):

    @property
    def provider_name(self):
        return 'psycopg2'

    def fetch_all(self, res):
        return res.fetchall()
