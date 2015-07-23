import mock


from hid.tables import ItemTable


def test_get_selected_returns_empty_list_on_empty_selection():
    params = mock.MagicMock()
    params.getlist.return_value = []

    assert ItemTable.get_selected(params) == []


def test_get_selected_returns_submitted_values_as_ints():
    params = mock.MagicMock()
    params.getlist.return_value = ["201", "199", "3"]

    assert ItemTable.get_selected(params) == [201, 199, 3]
