from django.http import QueryDict

from ..filters import AgeRangeFilter


def test_age_range_adds_taxonomy_terms():
    filter = AgeRangeFilter()

    filters = {}

    query_dict = QueryDict('age_range=Under 10 yrs&age_range=Age 11-14 yrs')

    filter.apply(filters, query_dict)

    assert 'age-ranges:Under 10 yrs' in filters['terms_or']
    assert 'age-ranges:Age 11-14 yrs' in filters['terms_or']
