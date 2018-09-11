""" This file defines a number of Javascript tests
    for a range of small javascript enhancements
    and utilities.

    Each feature should have it's own test class and
    test template.
"""
import pytest
from djangojs.runners import JsTemplateTestCase, QUnitSuite


@pytest.mark.phantomjs
class SelectAllCheckboxTest(QUnitSuite, JsTemplateTestCase):
    template_name = 'hid/tests/select_all_checkbox.html'
    js_files = (
        'js/jquery.min.js',
        'hid/js/select_all_checkbox.js'
    )
