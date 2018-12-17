from ..filters import AgeRangeFilter


def test_age_range_none_ignored():
    filter = AgeRangeFilter()

    filters = {}

    query_dict = {}

    filter.apply(filters, query_dict)

    assert 'from_age' not in filters
    assert 'to_age' not in filters


def test_age_range_blank_ignored():
    filter = AgeRangeFilter()

    filters = {}

    query_dict = {
        'from_age': '',
        'to_age': '',
    }

    filter.apply(filters, query_dict)

    assert 'from_age' not in filters
    assert 'to_age' not in filters
