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


class GenderFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        gender = query_dict.get('gender', None)
        if gender is not None:
            filters.update(gender=gender)


class AgeFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        age = query_dict.get('age', None)
        if age is not None:
            filters.update(age=age)


class EnnumeratorFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        ennumerator = query_dict.get('ennumerator', None)
        if ennumerator is not None:
            filters.update(ennumerator=ennumerator)


class SourceFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        source = query_dict.get('source', None)
        if source is not None:
            filters.update(source=source)
