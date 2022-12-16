from setuptools import setup, find_packages


def requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


def version():
    with open('./camelsp/__version__.py') as f:
        code = f.read()
    loc = dict()
    exec(code, loc, loc)
    return loc['__version__']

setup(
    name='camelsp',
    description='Camels data processing helper',
    author='Mirko Mälicke',
    author_email='mirko.maelicke@kit.edu',
    install_requires=requirements(),
    license='MIT',
    version=version(),
    packages=find_packages()
)