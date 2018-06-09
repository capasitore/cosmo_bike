from setuptools import setup, find_packages


with open('readme.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='cosmo_bike',
    version='1.0.0',
    description='Python Cosmo Bike package',
    #install_requires=required,
    long_description=readme,
    author='Efrain Calderon Estrada',
    author_email='darkcerano@gmail.com',
#    url='https://bitbucket.org/',
#    license=license,
    packages=find_packages(exclude=('tests', 'docs', 'resources'))
)