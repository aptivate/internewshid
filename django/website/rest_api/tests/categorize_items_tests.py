from __future__ import unicode_literals, absolute_import

import pytest

from django.core.urlresolvers import reverse
from rest_framework.test import APIRequestFactory
from data_layer.models import Item
from .item_create_view_tests import create_item
from .taxonomy_and_term_create_tests import (
    create_category,
    add_term,
)
from ..views import ItemViewSet


def categorize_item(item_id, taxonomy_slug, term_name):
    url = reverse('item-add-term', kwargs={"pk": item_id})
    term = {'taxonomy': taxonomy_slug, 'name': term_name}
    request = APIRequestFactory().post(url, term)
    view = ItemViewSet.as_view(actions={'post': 'add_term'})
    return view(request, item_pk=item_id)


@pytest.mark.django_db
def test_item_can_haz_category():
    # Create Taxonomy for Category-scheme
    category = create_category(name="Ebola Questions").data
    # Add terms (Categories)
    term = add_term(
        taxonomy=category["slug"],
        name="Vaccine",
    ).data
    # Create an Item
    item = create_item(body="Text").data

    # Associate category with the item
    categorize_item(
        item_id=item['id'],
        taxonomy_slug=category['slug'],
        term_name=term['name'],
    )

    # Fetch the item
    # TODO: use the API for this
    [item_orm] = Item.objects.all()

    # See the category
    [term_orm] = item_orm.terms.all()
    assert term_orm.name == 'Vaccine'


# TODO test for terms with the same name in different taxonomies
