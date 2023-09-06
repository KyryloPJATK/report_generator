import logging
import os
import shutil
from pprint import pprint
from typing import List

from report_generator_module.components.parsers.factory import ParsersFactory
from report_generator_module.components.parsers.base.strategy.function_call import FunctionParser
from report_generator_module.config import Configuration

logger = logging.getLogger(__name__)


ATTACHED_METHODS_PATH = f"./report_generator_module/components/parsers/base/attached_methods"


class ReportGenerator:

    @classmethod
    def run(cls,
            context: dict = None,
            config_files: List[str] = None,
            force_source_type: str = None):
        config = Configuration.create(source_files=config_files)
        source_type = force_source_type or config.get('source_path').split('.')[-1]
        ParsersFactory.run(source_type=source_type,
                           context=context,
                           config=config)

    @classmethod
    def attach_custom_methods(cls, name_to_file_path):

        for method_name, f_path in name_to_file_path.items():
            if os.path.exists(os.path.expanduser(f_path)):
                shutil.copyfile(f_path, os.path.join(ATTACHED_METHODS_PATH, f"{method_name}.py"))
                FunctionParser.attached_methods.append(method_name)
                pprint(f"Added attached method - {method_name}")
            else:
                raise FileNotFoundError(f"{f_path} does not exist")

    @classmethod
    def attach_custom_methods_from_dir(cls, path_to_dir: str):
        """
        List all python files in the specified directory.

        Parameters:
        - directory (str): The directory in which to search for files. Default is the current directory.

        Returns:
        - List[str]: A list of Python filenames.
        """
        files = [f.split(".py")[0] for f in os.listdir(path_to_dir)
                 if os.path.isfile(os.path.join(path_to_dir, f)) and f.endswith('.py')]
        return cls.attach_custom_methods({file: os.path.join(path_to_dir, file + ".py") for file in files})

    @classmethod
    def clean_up_attached_methods(cls):
        for f in os.listdir(ATTACHED_METHODS_PATH):
            file_path = os.path.join(ATTACHED_METHODS_PATH, f)
            if os.path.isfile(file_path) and f.endswith('.py'):
                os.remove(file_path)
                pprint(f"Removed attached method: {file_path}")
