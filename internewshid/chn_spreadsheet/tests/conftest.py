import pytest

from ..importer import Importer

COLUMN_LIST = [
    {
        'name': 'Province',
        'type': 'location',
        'field': 'message.location',
    },
    {
        'name': 'Message',
        'type': 'text',
        'field': 'message.content',
    },
]


@pytest.fixture
def importer():
    importer = Importer()

    importer.profile = {
        'columns': [d.copy() for d in COLUMN_LIST]
    }

    return importer
