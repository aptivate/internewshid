from collections import OrderedDict
from django.utils.translation import ugettext_lazy as _
from transport.taxonomies import term_itemcount


class TermCountChartWidget(object):
    """ A horizontal bar chart used to display number of entries for each
        term of a taxonomy.

        Settings:
            title: Name of the widget
            taxonomy: Slug of the taxonomy
            count: Maximum number of terms to display.
                   If this is >0, then only the countth most
                   used terms are displayed, and all others
                   are aggregated under 'Others'
            other_label: Optional label to use instead of 'Others'
    """
    template_name = 'hid/widgets/chart.html'
    javascript = [
        'flot/jquery.flot.js',
        'flot/jquery.flot.resize.js',
        'hid/widgets/chart.js'
    ]

    def _fetch_counts(self, taxonomy, count, other_label):
        """ Given a taxonomy, fetch the count per term.

        Args:
            - taxonomy: Taxonomy slug
            - count: If >0, maximum number of rows to returns. If the data
                     has more terms, all other terms are aggregated under
                     an 'others' section
            - other_label: Label for the 'Others' section
        """
        itemcount = term_itemcount(taxonomy)
        itemcount.sort(key=lambda k: int(k['count']), reverse=True)
        if count > 0:
            head = itemcount[0:count-1]
            tail = itemcount[count-1:]
        else:
            head = itemcount
            tail = []
        head.sort(key=lambda k: k['long_name'])
        counts = OrderedDict()
        for item in head:
            counts[item['long_name']] = item['count']
        if len(tail) > 0:
            agg = 0
            for item in tail:
                agg = agg + item['count']
            counts[other_label] = agg
        return counts

    def _create_axis_values(self, counts):
        """ Given a dictionary of label to value, create the Y and X axis values
            to be used in flot.

        Args:
            - chart: A dictionary of label to value

        Returns:
           A tuple containing (X Axis data, Y Axis data)
        """
        yticks = []
        values = []
        index = len(counts)
        for label, value in counts.items():
            yticks.append([index, label])
            values.append([value, index])
            index -= 1

        return values, yticks

    def get_context_data(self, **kwargs):
        title = kwargs.get('title', _('(missing title)'))
        taxonomy = kwargs.get('taxonomy')
        count = kwargs.get('count', 0)
        other_label = kwargs.get('other_label', 'Others')

        counts = self._fetch_counts(taxonomy, count, other_label)
        (values, yticks) = self._create_axis_values(counts)
        return {
            'title': title,
            'options': {
                'series': {
                    'bars': {
                        'show': True,
                        'fillColor': '#f29e30'
                    },
                    'color': 'transparent'
                },
                'bars': {
                    'horizontal': True,
                    'barWidth': 0.6,
                    'align': 'center',
                    'fill': True,
                    'lineWidth': 0,
                },
                'yaxis': {
                    'ticks': yticks,
                    'tickLength': 0,
                    'color': '#333333',
                    'font': {
                        'size': 12,
                        'style': 'normal',
                        'weight': 'normal',
                        'family': 'sans-serif'
                    }
                },
                'xaxis': {
                    'autoscaleMargin': 0.1
                },
                'grid': {
                    'hoverable': True,
                    'borderWidth': 0,
                    'margin': 10,
                    'labelMargin': 20,
                    'backgroundColor': '#fafafa'
                }
            },
            'data': [values]
        }
