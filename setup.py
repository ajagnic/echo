from setuptools import setup, find_packages

setup(
    name='echoterm',
    author='Adrian Agnic',
    url='https://github.com/ajagnic/echo/blob/master/tcp/clients/terminal.py',
    version='0.0.2',
    description='terminal client for echo tcp server',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pycrypto'],
    entry_points='''
    [console_scripts]
    echoterm=tcp.clients.terminal:main
    ''',
)