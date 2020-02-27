from django.contrib.messages import ERROR
from django.urls import reverse

from mock import Mock

from chn_spreadsheet.importer import SheetImportException

from ..views.upload_spreadsheet import UploadSpreadsheetView


class TestStorage(object):
    def add(self, level, message, extra_tags):
        self.extra_tags = extra_tags
        self.level = level
        self.message = message


def test_redirects_to_next_url_after_upload():
    next_url = reverse('tabbed-page',
                       kwargs={'name': 'main', 'tab_name': 'rumors'})

    view = UploadSpreadsheetView()
    view.request = Mock(POST={'next': next_url})

    url = view.get_success_url()

    assert url == next_url


def test_handles_sheet_import_exception():
    next_url = reverse('tabbed-page',
                       kwargs={'name': 'main', 'tab_name': 'rumors'})
    view = UploadSpreadsheetView()

    storage = TestStorage()

    view.request = Mock(POST={'next': next_url}, _messages=storage)

    error_message = "Something bad happened"
    store_spreadsheet = Mock(
        side_effect=SheetImportException(error_message)
    )
    importer = Mock(store_spreadsheet=store_spreadsheet)
    view.get_importer = Mock(return_value=importer)
    form = Mock(cleaned_data={'source': '', 'file': ''})

    view.form_valid(form)

    assert storage.message == "Something bad happened"
    assert storage.level == ERROR
