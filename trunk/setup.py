#!/usr/bin/env python

#from distutils.core import setup
#from setuptools import setup, find_packages
import sys, os

__license__ = 'GPL v.2 http://www.gnu.org/licenses/gpl.txt'
__author__ = "Gianluca Urgese <g.urgese@jasone.it>"
__version__ = '0.4'

# Distutils version
METADATA = dict(
	name = "pysusestudio",
	version = __version__,
	py_modules = ['pysusestudio'],
	author="Gianluca Urgese",
    author_email="g.urgese@jasone.it",
	description='Suse Studio python wrapper',
	long_description= open("README").read(),
	license=__license__,
	url='http://code.google.com/p/pysusestudio/',
	keywords='Suse Studio wrapper python library api',
	packages=['pysusestudio'],

)

# Setuptools version
SETUPTOOLS_METADATA = dict(
	install_requires = ['setuptools', 'simplejson', 'httplib2'],
	include_package_data = True,
	zip_safe=True,
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GPL License',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Internet',
	]
)

def Main():
	try:
		import setuptools
		METADATA.update(SETUPTOOLS_METADATA)
		setuptools.setup(**METADATA)
	except ImportError:
		import distutils.core
		distutils.core.setup(**METADATA)

if __name__ == '__main__':
  Main()