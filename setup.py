from setuptools import setup, find_packages

setup(
    name='mirrulations',
    version='0.0.0',
    python_requires='>=3.7.2',
    description='The objective of the Mirrulations project is to make the data on Regulations.gov more easily'
                'accessible to the public by acting as a mirror to the site.',
    long_description='Read README.md',
    author='Moravian College',
    author_email='colemanb@moravian.edu',
    url='https://github.com/MoravianCollege/mirrulations',
    packages=find_packages('src'),
    package_dir={'': 'src'}
)
