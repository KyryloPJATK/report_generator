import sys

from setuptools import setup, find_packages
from os import getenv, path


def compose_package_requirements():
    requirements = get_requirements("requirements.txt")
    if '--add-mysql' in sys.argv:
        requirements += get_requirements('mysql_requirements.txt')
    if '--add-postgres' in sys.argv:
        requirements += get_requirements('postgres_requirements.txt')
    return requirements


def get_requirements(requirements_filename: str):
    requirements_file = path.join(path.abspath(path.dirname(__file__)), "requirements", requirements_filename)
    with open(requirements_file, 'r', encoding='utf-8') as r:
        requirements = r.readlines()
    requirements = [r.strip() for r in requirements if r.strip() and not r.strip().startswith("#")]

    for i in range(0, len(requirements)):
        r = requirements[i]
        if "@" in r:
            parts = [p.lower() if p.strip().startswith("git+http") else p for p in r.split('@')]
            r = "@".join(parts)
            if getenv("GITHUB_TOKEN"):
                if "github.com" in r:
                    r = r.replace("github.com", f"{getenv('GITHUB_TOKEN')}@github.com")
            requirements[i] = r
    return requirements


with open("README.md", "r") as f:
    long_description = f.read()

with open("./version.py", "r", encoding="utf-8") as v:
    for line in v.readlines():
        if line.startswith("__version__"):
            if '"' in line:
                version = line.split('"')[1]
            else:
                version = line.split("'")[1]

setup(
    name='report_generator',
    version=version,
    description='Report Generator',
    url='https://github.com/KyryloPJATK/report_generator',
    author='Kyrylo Hrymailo',
    author_email='s17292@pjwstk.edu.pl',
    packages=find_packages(include=['report_generator_module', 'report_generator_module.*']),
    install_requires=compose_package_requirements(),
    zip_safe=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.8',
    ]
)
