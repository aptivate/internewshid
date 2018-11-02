class SimpleFilter(object):
    def __init__(self, filter_name):
        self.filter_name = filter_name

    def apply(self, filters, filter_value, **kwargs):
        filters[self.filter_name] = filter_value


class CategoryFilter(object):
    def apply(self, filters, filter_value, **kwargs):
        categories = kwargs.get('categories', None)

        if categories:
            filters.setdefault('terms', []).append(
                '{}:{}'.format(categories[0], filter_value)
            )
