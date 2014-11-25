#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name='scrapy-mongo-zhihu',
	version='0.1',
	description='',
	author='',
	url='',
	author_email='',
	packages = find_packages(),
	entry_points={'scrapy': ['settings = zhihu.settings']},
	install_requires = [
		'scrapy',
		'pymongo',
		'w3lib'	
	]
)
