from collections import OrderedDict
from datetime import timedelta

from django.conf import settings
from django.utils import dateformat
from django.utils.translation import ugettext_lazy as _

from dateutil import parser

from dashboard.widget_pool import WidgetError
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

    def _fetch_counts(self, taxonomy, count, start, end, other_label,
                      exclude_categories=None):
        """ Given a taxonomy, fetch the count per term.

        Args:
            taxonomy (str): Taxonomy slug
            count (int): If >0, maximum number of rows to returns. If the data
                has more terms, all other terms are aggregated under
                an 'others' section
            start (datetime or None): If not None, the start of the time period
                to get the count for
            end (datetime or None): If not None, the start of the time period
                to get the count for
            other_label (str): Label for the 'Others' section
        """
        itemcount = None
        if start is not None and end is not None:
            itemcount = term_itemcount(
                taxonomy, start_time=start, end_time=end
            )
        else:
            itemcount = term_itemcount(taxonomy)

        if exclude_categories is not None:
            itemcount = [t for t in itemcount
                         if t['name'] not in exclude_categories]

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

    def _create_date_range_label(self, start, end):
        """ Create a label to display a date range.

        The dates are formatter such that:
        - If either start or end include hours/minutes/seconds
          that are not 00:00:00 then the full date time is
          displayed;
        - If both start and end have zero hours/minutes/seconds
          then only the day is displayed, and the end day
          is set to the previous day (to show an inclusive
          range);

        Args:
            start (datetime): Start date time
            end (datetime): End date time
        Returns:
            str: Label to use for the date range.
        """
        if not start.time() and not end.time():
            start_str = dateformat.format(start,
                                          settings.SHORT_DATE_FORMAT)
            end_str = dateformat.format(end - timedelta(days=1),
                                        settings.SHORT_DATE_FORMAT)
        else:
            start_str = dateformat.format(start,
                                          settings.SHORT_DATETIME_FORMAT),
            end_str = dateformat.format(end,
                                        settings.SHORT_DATETIME_FORMAT)
        if start_str == end_str:
            return _('%(date)s') % {'date': start_str}
        else:
            return _('%(start)s - %(end)s') % {
                'start': start_str,
                'end': end_str
            }

    def get_context_data(self, **kwargs):
        title = kwargs.get('title', _('(missing title)'))
        taxonomy = kwargs.get('taxonomy')
        count = kwargs.get('count', 0)
        other_label = kwargs.get('other_label', 'Others')
        periods = kwargs.get('periods', [])
        exclude_categories = kwargs.get('exclude_categories')

        if len(periods) > 1:
            raise WidgetError('Only one time period is currently supported')
        if len(periods) == 1:
            try:
                start_time = parser.parse(periods[0]['start_time'])
                end_time = parser.parse(periods[0]['end_time'])
            except ValueError:
                raise WidgetError('Error parsing start/end time')
            legend = {
                'show': True,
                'noColumns': 1,
                'position': 'ne',
                'labelBoxBorderColor': 'white',
                'backgroundColor': 'white'
            }
            label = self._create_date_range_label(start_time, end_time)
        else:
            start_time = None
            end_time = None
            legend = {'show': False}
            label = ''

        counts = self._fetch_counts(
            taxonomy, count, start_time, end_time, other_label,
            exclude_categories
        )
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
                },
                'legend': legend
            },
            'data': [{
                'label': label,
                'color': '#f29e30',
                'data': values
            }]
        }
