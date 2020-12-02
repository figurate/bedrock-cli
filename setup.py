#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r") as readme:
    long_description = readme.read()

setup(
    name='bedrockcli',
    version_config={
        "version_format": "{tag}.dev{sha}",
        "starting_version": "0.9.0"
    },
    author='Ben Fortuna',
    author_email='fortuna@micronode.com',
    description='A tool for managing Terraform blueprints',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/micronode/bedrock-cli',
    packages=find_packages(),
    setup_requires=['better-setuptools-git-version'],
    install_requires=[
        'PyYAML>=5.3.1',
        'docker>=4.4.0',
        'dockerpty',
        'simple-term-menu'
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'bedrock = bedrock.cli:BedrockCli',
        ]
    }
)
