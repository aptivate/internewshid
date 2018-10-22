class CategoryFilter(object):
    def apply(self, filters, filter_value, **kwargs):
        categories = kwargs.get('categories', None)

        if categories:
            filters.setdefault('terms', []).append(
                '{}:{}'.format(categories[0], filter_value)
            )
