.. epsilon documentation master file, created by
   sphinx-quickstart on Sat Feb 24 10:59:55 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to epsilon's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Usage
=====

To create a regular expression programmatically, follow these steps:

.. doctest::

    >>> from epsilon.regex import unicode
    >>> e = unicode.Expression.EPSILON
    >>> e
    Epsilon()
    >>> e.nu()
    Epsilon()


Reference
=========

.. automodule:: epsilon
    :members:


# .. automodule:: epsilon.parse
#    :members:


# .. autoclass:: epsilon.parse.Parser
#    :members:

.. autoclass:: epsilon.parse.SyntaxError
    :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
