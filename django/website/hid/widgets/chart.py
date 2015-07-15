class QuestionChartWidget(object):
    """ A horizontal bar chart used to display quantitative answers to
        specific questions.

        Eventually this should pull the questions and values from the
        data API. For now we pass these in via the settings.

        Settings:
            name: Name of the chart
            questions: Dictionary of question to value
    """
    template_name = 'hid/widgets/chart.html'
    javascript = [
        'flot/jquery.flot.js',
        'flot/jquery.flot.resize.js',
        'hid/widgets/chart.js'
    ]

    def get_context_data(self, **kwargs):
        index = 0
        yticks = []
        values = []
        for question, answer in kwargs['questions'].items():
            yticks.append([index, question])
            values.append([answer, index])
            index += 1

        return {
            'name': kwargs['name'],
            'options': {
                'series': {
                    'bars': {
                        'show': True,
                        'fillColor': '#0B62A4'
                    },
                    'color': '#0B62A4'
                },
                'bars': {
                    'horizontal': True,
                    'barWidth': 0.5,
                    'align': 'center',
                    'fill': True,
                    'lineWidth': 1,
                },
                'yaxis': {
                    'ticks': yticks,
                    'tickLength': 0,
                    'color': '#282625',
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
                    'hoverable': True
                }
            },
            'data': [values]
        }