import pytest

from ..models import SheetProfile


@pytest.mark.django_db
def test_unicode_is_label():
    profile = SheetProfile.objects.create(label='Test')

    assert str(profile) == 'Test'
