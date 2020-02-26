import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory

from data_layer.models import Item

from ..views import ItemViewSet


def categorize_item(item, term):
    request = APIRequestFactory().post("", term)
    view = ItemViewSet.as_view(actions={'post': 'add_terms'})
    return view(request, item_pk=item['id'])


@pytest.mark.django_db
def test_item_can_haz_category(vaccine_term, item):
    # Associate category with the item
    categorize_item(item, vaccine_term)

    # Fetch the item
    # TODO: use the API for this
    [item_orm] = Item.objects.all()
    # See the category
    [term_orm] = item_orm.terms.all()
    assert term_orm.name == vaccine_term['name']


# TODO test for terms with the same name in different taxonomies

@pytest.mark.django_db
def test_categorize_item_returns_the_categorized_item(vaccine_term, item):
    result = categorize_item(item, vaccine_term).data

    assert result['id'] == item['id']
    terms = result['terms']
    assert vaccine_term in terms


@pytest.mark.django_db
def test_categorize_item_fails_gracefully_if_taxonomy_not_found(item):
    response = categorize_item(
        item,
        {'taxonomy': 'unknown-slug', 'name': 'unknown-term'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "Taxonomy matching query does not exist."


@pytest.mark.django_db
def test_categorize_item_fails_gracefully_if_term_not_found(item, category):
    response = categorize_item(
        item,
        {'taxonomy': category.slug, 'name': 'unknown-term'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'] == "Term matching query does not exist."


@pytest.mark.django_db
def test_categorize_item_fails_gracefully_if_item_not_found(vaccine_term, item):
    unknown_item_id = 6  # I am not a prisoner
    response = categorize_item({'id': unknown_item_id}, vaccine_term)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == "Message matching query does not exist."


@pytest.mark.django_db
def test_only_one_category_per_item_per_taxonomy(item, vaccine_term,
                                                 timescales_term):
    """
        At the time of writing, all taxonomies are categories
        so there's no need yet to test that the taxonomy is a
        catagory one. Ultimately this test  sould be called something like
        test_cardinality_constraints_on_taxonomies, and maybe move them
        all to their own file. They should set the cardinality constraint
        on the Taxonmy object to optional for these tests.
    """
    categorize_item(item, vaccine_term)
    categorize_item(item, timescales_term)

    # TODO: use the API for this
    [item_orm] = Item.objects.all()
    terms = item_orm.terms.all()
    assert len(terms) == 1
    assert terms[0].name == timescales_term['name']
