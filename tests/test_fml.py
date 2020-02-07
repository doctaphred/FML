import pytest


def test_something():
    z = z['z'] = {}
    assert repr(z) == "{'z': {...}}"

    t = (2, [3, 4])
    with pytest.raises(TypeError):
        t[1] += [10, 11]
    assert t == (2, [3, 4, 10, 11])
