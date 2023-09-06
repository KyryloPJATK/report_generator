import json
import logging
import os
from typing import List

logger = logging.getLogger(__name__)


class Configuration:
    """ Generic configuration module"""
    env = os.environ.get('ENV', 'DEV')

    def __init__(self):
        self.config_data = dict()

    def init_config_data(self, source_files: List[str]):
        # Warning: Calling this method will erase existing config data
        self.config_data = dict()
        for source_file in [file for file in list(set(source_files)) if file]:
            self.add_new_config_properties(Configuration.extract_config_from_path(source_file))

    def add_new_config_properties(self, new_config_dict: dict, at_key: str = None):
        """
            Adds new configuration properties to existing configuration dict

            :param new_config_dict: dictionary containing new configuration
            :param at_key: the key at which to append new dictionary
                            (optional but setting that will reduce possible future key conflicts)
        """
        if at_key:
            self.config_data[at_key] = new_config_dict
        else:
            # merge existing config with new dictionary (python 3.5+ syntax)
            self.config_data = {**self.config_data, **new_config_dict}

    def get(self, key, default=None):
        return self.config_data.get(self.env, {}).get(key, default)

    def get_db_properties_by_alias(self, alias: str):
        """Gets DB configuration by alias"""
        db_config = self.get('DATABASE_CONFIG', {})
        alias = alias or db_config.get('__default_alias')
        if alias:
            return db_config.get(alias, {})

    @classmethod
    def create(cls, source_files: List[str] = None):
        default_config_file = os.path.expanduser(os.environ.get('REPORT_GENERATOR_CONFIG', ""))
        source_files = source_files or [default_config_file]
        config = Configuration()
        config.init_config_data(source_files=source_files)
        return config

    @staticmethod
    def extract_config_from_path(file_path: str) -> dict:
        """
            Extracts configuration dictionary from desired file path

            :param file_path: desired file path

            :returns dictionary containing configs from target file, empty dict otherwise
        """
        try:
            with open(os.path.expanduser(file_path)) as input_file:
                extraction_result = json.load(input_file)
        except Exception as ex:
            logger.error(f'Exception occurred while extracting data from {file_path}: {ex}')
            extraction_result = dict()
        return extraction_result
