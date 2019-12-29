from distutils.core import setup

setup(
    name='wellness-tracker',
    version='0.0',
    packages=['Models', 'templates.utilities', 'templates.visualization'],
    package_dir={'': 'wellness-tracker'},
    url='',
    license='',
    author='Evan Meikleham',
    author_email='evanakm@protonmail.com',
    description='',
    install_requires=['flask-bootstrap']
)
