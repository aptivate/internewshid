from django.urls import reverse

from mock import Mock

from ..views.upload_spreadsheet import UploadSpreadsheetView


def test_redirects_to_next_url_after_upload():
    next_url = reverse('tabbed-page',
                       kwargs={'name': 'main', 'tab_name': 'rumors'})

    view = UploadSpreadsheetView()
    view.request = Mock(POST={'next': next_url})

    url = view.get_success_url()

    assert url == next_url
