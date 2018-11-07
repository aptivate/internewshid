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
        tags = kwargs.get('tags', None)
        if tags is not None:
            filters.update(tags=tags)


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
