class CategoryFilter(object):
    def apply(self, filters, query_dict, **kwargs):
        category = query_dict.get('category', None)
        categories = kwargs.get('categories', None)

        if category and categories:
            filters.setdefault('terms', []).append(
                '{}:{}'.format(categories[0], category)
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
