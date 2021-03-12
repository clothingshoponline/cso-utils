from setuptools import setup

package = dict()
with open('cso_utils/__version__.py', 'r') as f:
    version_data = f.read()
for line in version_data.split('\n'):
    key, value = line.split(' = ')
    package[key] = value.replace("'", '').strip()


setup(name=package['__title__'],
      version=package['__version__'],
      author=package['__author__'],
      packages=[package['__title__']],
      python_requires=package['__pyversion__'],
      install_requires=[package['__requests__'], 
                        package['__pygithub__']]
)