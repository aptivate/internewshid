import datetime

import pytest
from rest_framework.exceptions import ValidationError

import transport

from ..serializers import ItemSerializer


@pytest.mark.django_db
def test_serialized_timestamp_ignores_microseconds():
    data = {
        'body': "Test",
        'timestamp': datetime.datetime.now().replace(microsecond=123)
    }

    transport.items.create(data)

    data['timestamp'] = data['timestamp'].replace(microsecond=0)

    serializer = ItemSerializer(data=data)

    with pytest.raises(ValidationError) as e:
        serializer.is_valid(raise_exception=True)
