# tests/conftest.py
from spidermon import Monitor


def pytest_pycollect_makeitem(collector, name, obj):
    try:
        if issubclass(obj, Monitor):
            return []
    except TypeError:
        pass
