Modules Overview
================

Individual modules that come with this project are not exposed directly. However, there are a few worth being discussed here due to their agnostic qualities allowing for an application outside of the scope of microanalyst as well as to better understand and utilize them.

expression.py
-------------

Defines a flexible wrapper around Python's lambda function which can be evaluated dynamically::

    >>> from microanalyst.model.expression import Expression
    >>> is_even = Expression('x % 2 == 0')
    >>> print is_even
    x % 2 == 0
    >>> print is_even(2)
    True

The optional ``scope`` allows to evaluate custom variables::

    >>> scope = {'is_even': is_even}
    >>> is_odd = Expression('not is_even(x)', scope)
    >>> print is_odd(3)
    True

Use ``locals()`` to refer to variables in the current scope::

    >>> is_even = Expression('x % 2 == 0')
    >>> is_odd = Expression('not is_even(x)', locals())

Use ``globals()`` and forward declarations for recursive calls::

    >>> expr = '1 if n < 2 else fib(n - 2) + fib(n - 1)'
    >>> global fib
    >>> fib = Expression(expr, globals(), ('n',))
    >>> print fib(11)
    144

Enforce parameter order with explicit ``params``::

    >>> pp = Expression('(x/z, y/z)', params=('x', 'y', 'z'))
    >>> x, y = pp(10, 25, 5)

stylesheet.py
-------------

Minimalist syntax for XF records (Microsoft® Excel™ cell formatting) inspired by Cascading Style Sheets (CSS).

Supported properties
^^^^^^^^^^^^^^^^^^^^

* background-color
* border-color
* color
* font-weight
* text-align
* number-format (non-standard)

Supported selectors
^^^^^^^^^^^^^^^^^^^

* wildcard ``*``
* class selector, e.g. ``.header``
* combined selectors, e.g. ``.header, .footer``

Styles can be commented out with multi-line comments enclosed between ``/*`` and ``*/`` which can be nested.

XF records are cached due to the upper limit of 4k in a single xls file.

Sample usage::

 >>> from microanalyst.xls import stylesheet
 >>> style = stylesheet.load('colorful.css')
 >>> for i in range(5):
 >>>     xf = style('.header.big', alt=i % 2)

tkwidgets.py
------------

User friendly wrappers over new-style and legacy Tkinter widgets.

**TODO**

uniutils.py
-----------

Miscellaneous utilities for Unicode handling which strive to maintain portability across the three major platforms, i.e. Windows, Linux and Mac OS. Despite the 21st century character encoding still remains an issue justifying the need for such a module.

File system, shell and stdin/stdout/stderr may all have different character encodings even on a single platform. Furthermore, these encodings vary depending on the language version of the operating system.

Unfortunatley, the sole character encoding is not sufficient to retain portability either. For example both Linux and Mac OS can use the same UTF-8 encoding for file system but in different normal forms (NFC vs. NFD), which has to be taken into account and addressed accordingly.