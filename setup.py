from setuptools import setup, find_packages

INSTALL_REQUIRES = ['requests==2.21.0',
                    'flask==1.0.2',
                    'redis==3.1.0',
                    'python-redis-lock==3.3.1',
                    'pytest==4.3.0',
                    'pytest-cov==2.6.1',
                    'pycodestyle==2.5.0',
                    'fakeredis[lua]==1.0.2',
                    'mock==2.0.0',
                    'requests-mock==1.5.2']

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
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points={'console_scripts': ['mirrulations=mirrulations_core.__main__:main',
                                      'mirrulations-queue-check=mirrulations_server.redis_mananger:print_queue']}
)
