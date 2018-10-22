import pytest

from ..filter_pool import (
    MissingFilterError, clear_filters, get_filter, register_filter
)


class TestFilter(object):
    pass


@pytest.fixture
def filter():
    return TestFilter()


def setup_function(function):
    clear_filters()


def test_filter_is_registered(filter):
    register_filter('test-filter', filter)
    assert get_filter('test-filter') == filter


def test_exception_when_filter_not_registered(filter):
    with pytest.raises(MissingFilterError) as excinfo:
        get_filter('test-filter')

    assert "Filter named 'test-filter' has not been registered" in str(
        excinfo.value)


def test_registering_twice_overrides_existing_filter(filter):
    register_filter('test-filter', filter)

    filter2 = TestFilter()
    register_filter('test-filter', filter2)

    assert get_filter('test-filter') == filter2
