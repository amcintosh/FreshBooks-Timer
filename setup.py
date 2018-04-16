from setuptools import setup, find_packages
import fbtimer

setup(
    name='fbtimer',
    version=fbtimer.__version__,
    author=fbtimer.__author__,
    author_email='andrew@amcintosh.net',
    description='Track time in FreshBooks via the command line',
    long_description=open('README.rst').read(),
    url='https://github.com/amcintosh/FreshBooks-Timer',
    download_url='https://github.com/amcintosh/FreshBooks-Timer/archive/{}.tar.gz'.format(
        fbtimer.__version__),
    keywords=['FreshBooks', 'Time Tracking'],
    license=fbtimer.__license__,
    packages=find_packages(exclude=['*.test', '*.test.*']),
    include_package_data=True,
    install_requires=open('requirements.txt').readlines(),
    entry_points={
        'console_scripts': [
            'fbtimer=fbtimer.cli:cli'
        ]
    },
    setup_requires=['pytest-runner', ],
    tests_require=['pytest', ],
    test_suite='tests'
)
