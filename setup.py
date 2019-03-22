from setuptools import setup, find_packages

CORE_REQUIRES = ['requests==2.21.0']
CLIENT_REQUIRES = []
SERVER_REQUIRES = ['flask==1.0.2',
                   'redis==3.1.0',
                   'python-redis-lock==3.3.1']
WEB_REQUIRES = []
DEV_REQUIRES = ['pytest==4.3.0',
                'fakeredis[lua]==1.0.2',
                'mock==2.0.0',
                'requests-mock==1.5.2']
INSTALL_REQUIRES = CORE_REQUIRES + CLIENT_REQUIRES + SERVER_REQUIRES + WEB_REQUIRES
TESTS_REQUIRE = INSTALL_REQUIRES + DEV_REQUIRES

setup(
    name='mirrulations',
    version='0.0.0',
    description='The objective of the Mirrulations project is to make the data on Regulations.gov more easily'
                'accessible to the public by acting as a mirror to the site.',
    long_description='Read README.md',
    author='Moravian College',
    author_email='colemanb@moravian.edu',
    url='https://github.com/MoravianCollege/mirrulations',
    python_requires='>=3.7.2',
    install_requires=INSTALL_REQUIRES,
    test_suite='pytest',
    tests_require=TESTS_REQUIRE,
    extras_require={'dev': DEV_REQUIRES},
    packages=find_packages('src'),
    package_dir={'': 'src'},
    data_files={('.config', ['.config/config.ini', '.config/moved_config.ini', '.config/example.ini'])},
    entry_points={'console_scripts': ['mirrulations-client=mirrulations_client.__main__:main',
                                      'mirrulations-server=mirrulations_server.__main__:main',
                                      'mirrulations-web=mirrulations_web.__main__:main',
                                      'mirrulations-queue-check=mirrulations_server.redis_mananger:print_queue']}
)
