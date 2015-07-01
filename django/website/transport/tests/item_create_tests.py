import pytest


@pytest.mark.xfail
def test_create_message_creates_item():
    # now = timezone.now().replace(
    #     microsecond=0  # MySQL discards microseconds
    # )
    # item = {'body': "Text", 'timestamp': now}
    # dl.create_message(item)
    # create.assert_called_with(message)
    assert False
