def function_with_doctests():
    """These should be picked up by pytest.

    >>> z = z['z'] = {}
    >>> z
    {'z': {...}}

    >>> t = (2, [3, 4])
    >>> t[1] += [10, 11]
    Traceback (most recent call last):
      ...
    TypeError: 'tuple' object does not support item assignment
    >>> t
    (2, [3, 4, 10, 11])
    """
    pass
