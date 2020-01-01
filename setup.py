#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0',
                'bcrypt>=3.1.7',
                'python-dateutil>=2.8.0',
                'bokeh>=1.4.0',
                'flask_bootstrap>=3.3.7',
                'pymongo>=3.9.0',
                'Flask>=1.1.1',
                'Flask-Bootstrap>=3.3.7',
                'Flask-WTF>=0.14.2',
                'flask-nav>=0.6'
                ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Evan Meikleham",
    author_email='evanakm@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Tracks and visualizes vital data",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='wellness_tracker',
    name='wellness_tracker',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/evanakm/wellness-tracker',
    version='0.1.0',
    zip_safe=False,
)
