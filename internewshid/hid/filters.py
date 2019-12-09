class CategoryFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        category = query_dict.get('category', None)
        categories = kwargs.get('categories', None)

        if category and categories:
            filters.setdefault('terms', []).append(
                '{}:{}'.format(categories[0], category)
            )


class TagsFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        tags = query_dict.get('tags', None)
        if tags is not None:
            filters.setdefault('terms', []).append(
                'tags:{}'.format(tags)
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
        from_age = self.get_int_value(query_dict, 'from_age')
        to_age = self.get_int_value(query_dict, 'to_age')

        if from_age is not None and to_age is not None:
            filters.update(
                from_age=from_age,
                to_age=to_age
            )

    def get_int_value(self, query_dict, name):
        value = query_dict.get(name, None)

        if value is None:
            return None

        try:
            return int(value)

        except ValueError:
            return None


class EnumeratorFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        enumerator = query_dict.get('enumerator', None)
        if enumerator is not None:
            filters.update(enumerator=enumerator)


class SourceFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        source = query_dict.get('source', None)
        if source is not None:
            filters.update(source=source)


class FeedbackTypeFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        feedback_type = query_dict.get('feedback_type', None)

        if feedback_type:
            filters.setdefault('terms', []).append(
                'item-types:{}'.format(feedback_type)
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
