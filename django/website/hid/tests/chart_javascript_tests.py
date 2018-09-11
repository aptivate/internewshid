from djangojs.runners import QUnitSuite, JsTemplateTestCase

import pytest


@pytest.mark.phantomjs
class ChartJavascriptTest(QUnitSuite, JsTemplateTestCase):
    template_name = 'hid/tests/chart.html'
    js_files = (
        'js/jquery.min.js',
        'js/underscore.js',
        'js/backbone.js',
        'flot/jquery.flot.js',
        'flot/jquery.flot.resize.js',
        'hid/widgets/chart.js'
    )
