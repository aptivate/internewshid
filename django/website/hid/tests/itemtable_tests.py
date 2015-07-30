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


def test_get_row_select_values_returns_id_value_pairs():
    post_params = {
        'category-123': "second",
        'category-99': "third",
        'category-56': "first",
        'category-1': "second",
    }
    expected = [
        (123, "second"),
        (99, "third"),
        (56, "first"),
        (1, "second")
    ]
    actual = ItemTable.get_row_select_values(post_params, 'category')
    assert sorted(expected) == sorted(actual)  # Order is not important


def test_get_row_select_values_reads_params_from_prefix():
    post_params = {
        'prefix-123': "second",
        'prefix-99': "third",
        'other-1': "second",
    }
    expected = [
        (123, "second"),
        (99, "third"),
    ]
    actual = ItemTable.get_row_select_values(post_params, 'prefix')
    assert sorted(expected) == sorted(actual)  # Order is not important


def test_get_row_select_values_removes_empty():
    post_params = {
        'category-123': "second",
        'category-99': "third",
        'category-56': "",
    }
    expected = [
        (123, "second"),
        (99, "third"),
    ]
    actual = ItemTable.get_row_select_values(post_params, 'category')
    assert sorted(expected) == sorted(actual)  # Order is not important
