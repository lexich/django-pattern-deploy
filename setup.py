from setuptools import setup, find_packages

setup(
	name="Django pattern deploy",
	version="0.0.2",
	url="https://github.com/lexich/django-pattern-deploy",
	author="lexich",
	scripts=["django-pattern-deploy.py",],
	packages=find_packages()
	)
