from setuptools import setup, find_packages

setup(
	name="Django pattern deploy",
	version="0.0.7",
	url="https://github.com/lexich/django-pattern-deploy",
	author="lexich",
	install_requires=[
		"virtualenv"		
	],
	scripts=["django-pattern-deploy.py",],
	packages=find_packages()
	)
