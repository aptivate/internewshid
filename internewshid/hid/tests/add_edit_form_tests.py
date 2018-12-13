from mock import patch

from ..forms.item import AddEditItemForm


def test_form_does_not_have_category_field_if_not_defined():
    item_type_category = {
    }
    with patch('hid.forms.item.ITEM_TYPE_CATEGORY', item_type_category):
        form = AddEditItemForm()
        assert 'category' not in form.fields


def test_form_does_have_category_field_if_defined():
    item_type_category = {
        'all': 'some-taxonomy'
    }
    with patch('hid.forms.item.ITEM_TYPE_CATEGORY', item_type_category):
        with patch('hid.forms.item.transport.terms.list') as term_list:
            term_list.return_value = []
            form = AddEditItemForm()
            assert 'category' in form.fields


def test_form_category_has_expected_choices():
    item_type_category = {
        'some-item-type': 'some-taxonomy'
    }
    with patch.dict('hid.forms.item.ITEM_TYPE_CATEGORY', item_type_category):
        with patch('hid.forms.item.transport.terms.list') as term_list:
            term_list.return_value = [
                {
                    'taxonomy': 'some-taxonomy',
                    'name': 'name1',
                    'long_name': 'long name one'
                },
                {
                    'taxonomy': 'some-taxonomy',
                    'name': 'name2',
                    'long_name': 'long name two'
                },
            ]
            expected_choices = [
                ('', '-----'),
                ('name1', 'name1'),
                ('name2', 'name2')
            ]
            form = AddEditItemForm('some-item-type')
            assert 'category' in form.fields
            assert form.fields['category'].choices == expected_choices


def test_category_field_is_not_required():
    item_type_category = {
        'some-item-type': 'some-taxonomy'
    }
    with patch.dict('hid.forms.item.ITEM_TYPE_CATEGORY', item_type_category):
        with patch('hid.forms.item.transport.terms.list') as term_list:
            term_list.return_value = []
            form = AddEditItemForm('some-item-type')

    assert not form.fields['category'].required
