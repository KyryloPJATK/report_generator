import argparse
import json

from report_generator_module.controller import ReportGenerator


def load_context_from_file(context_file_path: str):
    with open(context_file_path, 'r') as f:
        data = json.load(f)
    return data


def parse_args():
    parser = argparse.ArgumentParser(description='CLI Properties to run Report Generator.')

    parser.add_argument('--context_data', type=str, required=True, help='JSON file path containing running context')
    parser.add_argument('--config_data', type=str, required=True, nargs='+', help='JSON file path containing config data')
    parser.add_argument('--extra_attached_methods', type=str, help='path to additional methods to attach (optional)')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    if args.extra_attached_methods:
        ReportGenerator.clean_up_attached_methods()
        ReportGenerator.attach_custom_methods_from_dir(path_to_dir=args.extra_attached_methods)
    ReportGenerator.run(context=load_context_from_file(args.context_data),
                        config_files=args.config_data)
