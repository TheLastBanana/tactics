def clamp(x, a, b):
    """
    Clamps x between the values of a and b, where a <= x <= b.
    Clever method shamelessly stolen from
    http://stackoverflow.com/questions/4092528/how-to-clamp-an-integer-to-some-
    range-in-python
    
    >>> clamp(10, 0, 5)
    5
    >>> clamp(-7, -5, 5)
    -5
    >>> clamp(3, -10, 10)
    3
    
    """
    return min(b, max(x, a))
