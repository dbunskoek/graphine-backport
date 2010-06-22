#! /usr/bin/env python

from distutils.core import setup

setup(name='Graphine backport',
    version='0.0',
    description='a backport of this highly flexible graph library to Python 2.x',
    author='Dennis Bunskoek',
    author_email='dbunskoek@leukeleu.nl',
    url='http://www.graphine.org',
    packages=['graph', 'graph.extras']
)
