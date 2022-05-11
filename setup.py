from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in its_charging/__init__.py
from its_charging import __version__ as version

setup(
	name="its_charging",
	version=version,
	description="Connection to EWSE",
	author="itsdave",
	author_email="h",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
