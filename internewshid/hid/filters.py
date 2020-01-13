class CategoryFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        category = query_dict.get('category', None)
        categories = kwargs.get('categories', None)

        if category and categories:
            filters.setdefault('terms', []).append(
                '{0}:{1}'.format(categories[0], category)
            )


class TagsFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        tags = query_dict.get('tags', None)
        if tags is not None:
            filters.setdefault('terms', []).append(
                'tags:{0}'.format(tags)
            )


class TimeRangeFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        start_time = query_dict.get('start_time', None)
        end_time = query_dict.get('end_time', None)

        if start_time and end_time:
            filters.update(
                start_time=start_time,
                end_time=end_time
            )


class LocationFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        location = query_dict.get('location', None)
        if location is not None:
            filters.update(location=location)


class SubLocationFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        sub_location = query_dict.get('sub-location', None)
        if sub_location is not None:
            filters.update(sub_location=sub_location)


class GenderFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        gender = query_dict.get('gender', None)
        if gender is not None:
            filters.update(gender=gender)


class AgeRangeFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        age_range_terms = []

        for age_range in query_dict.getlist('age_range', []):
            age_range_terms.append('age-ranges:{}'.format(age_range))

        filters['terms_or'] = filters.get('terms_or', []) + age_range_terms


class EnumeratorFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        enumerator = query_dict.get('enumerator', None)
        if enumerator is not None:
            filters.update(enumerator=enumerator)


class CollectionTypeFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        collection_type = query_dict.get('collection_type', None)
        if collection_type is not None:
            filters.update(collection_type=collection_type)


class FeedbackTypeFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        feedback_type = query_dict.get('feedback_type', None)

        if feedback_type:
            filters.setdefault('terms', []).append(
                'item-types:{0}'.format(feedback_type)
            )


class ExternalIdFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        pattern = query_dict.get('external_id_pattern', None)

        if pattern:
            filters.update(external_id_pattern=pattern)


class SearchFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        search = query_dict.get('search', None)

        if search:
            filters.update(search=search)
