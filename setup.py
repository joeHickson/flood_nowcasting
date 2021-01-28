# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    requirements = f.read()

setup(
    name='flood_nowcasting',
    version='0.1.0',
    description='Flood nowcasting script',
    long_description=readme,
    author='Joe Hickson',
    url='https://github.com/joehickson/flood_nowcasting',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=requirements
)
