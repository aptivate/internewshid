from django.template import Context

import mock

from hid.constants import ITEM_TYPE_CATEGORY
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


def test_get_row_select_values_does_not_remove_empty():
    post_params = {
        'category-123': "second",
        'category-99': "third",
        'category-56': "",
    }
    expected = [
        (123, "second"),
        (99, "third"),
        (56, ""),
    ]
    actual = ItemTable.get_row_select_values(post_params, 'category')
    assert sorted(expected) == sorted(actual)  # Order is not important


@mock.patch('hid.tables.loader')
def test_render_category_passes_context_to_template(mock_loader):
    mock_template = mock.MagicMock()
    mock_template.render = mock.MagicMock()
    mock_loader.get_template = mock.MagicMock(
        return_value=mock_template)

    value = [
        {
            u'long_name': u'Repatriation',
            u'name': u'Repatriation',
            u'taxonomy': ITEM_TYPE_CATEGORY['all'],
        }
    ]

    categories = (
        ('Repatriation', 'Repatriation'),
        ('Pregnancy', 'Pregnancy'),
        ('Safety', 'Safety'),
    )

    table = ItemTable([], categories=categories)

    record = mock.Mock()
    table.render_category(record, value)

    context = {
        'categories': categories,
        'selected': ['Repatriation'],
        'record': record,
    }

    mock_template.render.assert_called_with(context)


@mock.patch('hid.tables.loader')
def test_render_tags_passes_record_and_tags_to_template(mock_loader):
    mock_template = mock.MagicMock()
    mock_template.render = mock.MagicMock()
    mock_loader.get_template = mock.MagicMock(
        return_value=mock_template)

    record = {
        'terms': [
            {
                'name': 'foo',
                'taxonomy': 'tags',
            },
            {
                'name': 'bar',
                'taxonomy': 'tags',
            },
            {
                'name': 'baz',
                'taxonomy': 'not tags',
            },
        ]
    }

    table = ItemTable([], categories=None)
    table.context = Context()

    table.render_tags(record, None)

    args, kwargs = mock_template.render.call_args

    assert args[0]['record'] == record
    assert args[0]['tags'] == 'Foo, Bar'


@mock.patch('hid.tables.loader')
def test_render_feedback_type_passes_context_to_template(mock_loader):
    mock_template = mock.MagicMock()
    mock_template.render = mock.MagicMock()
    mock_loader.get_template = mock.MagicMock(
        return_value=mock_template)

    value = [
        {
            u'long_name': u'Rumour',
            u'name': u'rumour',
            u'taxonomy': 'item-types',
        },
        {
            u'long_name': u'Concern',
            u'name': u'concern',
            u'taxonomy': 'item-types',
        }
    ]

    table = ItemTable([])
    table.context = Context()

    record = mock.Mock()
    table.render_feedback_type(record, value)

    args, kwargs = mock_template.render.call_args

    assert args[0]['record'] == record
    assert args[0]['feedback_type'] == 'Concern, Rumour'


@mock.patch('hid.tables.loader')
def test_render_age_range_passes_context_to_template(mock_loader):
    mock_template = mock.MagicMock()
    mock_template.render = mock.MagicMock()
    mock_loader.get_template = mock.MagicMock(
        return_value=mock_template)

    value = [
        {
            u'long_name': u'Age 11-14 yrs',
            u'name': u'Age 11-14 yrs',
            u'taxonomy': 'age-ranges',
        },
        {
            u'long_name': u'Age 15-18 yrs',
            u'name': u'Age 15-18 yrs',
            u'taxonomy': 'age-ranges',
        }
    ]

    table = ItemTable([])
    table.context = Context()

    record = mock.Mock()
    table.render_age_range(record, value)

    args, kwargs = mock_template.render.call_args

    assert args[0]['record'] == record
    assert args[0]['age_ranges'] == 'Age 11-14 yrs, Age 15-18 yrs'


def test_total_items_is_count_of_items_if_none():
    table = ItemTable(['one', 'two', 'three'])

    assert table.total_items == 3


def test_total_items_is_set_from_kwarg():
    table = ItemTable(['one', 'two', 'three'],
                      total_items=10)

    assert table.total_items == 10


def test_page_range_for_first_of_few_pages():
    table = ItemTable(['one', 'two', 'three'],
                      per_page=3,
                      page_number=1,
                      total_items=10)

    assert table.page_range == [1, 2, 3]


def test_page_range_for_first_of_lots_of_pages():
    table = ItemTable(['one', 'two', 'three'],
                      per_page=3,
                      page_number=1,
                      total_items=100)

    assert table.page_range == [1, 2, 3, 4, '...', 33]


def test_page_range_for_middle_of_lots_of_pages():
    table = ItemTable(['one', 'two', 'three'],
                      per_page=3,
                      page_number=15,
                      total_items=100)

    assert table.page_range == [1, '...', 14, 15, '...', 33]


def test_page_range_for_last_of_lots_of_pages():
    table = ItemTable(['one', 'two', 'three'],
                      per_page=3,
                      page_number=33,
                      total_items=100)

    assert table.page_range == [1, '...', 30, 31, 32, 33]
