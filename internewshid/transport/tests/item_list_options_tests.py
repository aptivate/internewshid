import pytest
from django_dynamic_fixture import G

from data_layer.models import Item
from transport.items import list_options


@pytest.mark.django_db
def test_list_options_for_gender_retrieved_all_options():
    items = G(Item, n=5)
    expected_genders = [an_item.gender for an_item in items]
    actual_genders = list(list_options('gender'))
    assert expected_genders == actual_genders


@pytest.mark.django_db
def test_list_options_for_gender_unique():
    G(Item, gender='male', n=2)
    G(Item, gender='female', n=2)
    G(Item, gender='xie')
    expected_genders = ['female', 'male', 'xie']
    actual_genders = list(list_options('gender'))
    assert expected_genders == actual_genders


@pytest.mark.django_db
def test_list_options_for_gender_exclude_blank():
    G(Item, gender='', n=2)
    G(Item, gender='female', n=2)
    G(Item, gender='xie')
    expected_genders = ['female', 'xie']
    actual_genders = list(list_options('gender'))
    assert expected_genders == actual_genders


@pytest.mark.django_db
def test_list_options_for_location_retrieved_all_options():
    items = G(Item, n=5)
    expected_locations = [an_item.location for an_item in items]
    actual_locations = list(list_options('location'))
    assert expected_locations == actual_locations


@pytest.mark.django_db
def test_list_options_for_location_unique():
    G(Item, location='Cambridge', n=2)
    G(Item, location='Brighton', n=2)
    G(Item, location='London')
    expected_locations = ['Brighton', 'Cambridge', 'London']
    actual_locations = list(list_options('location'))
    assert expected_locations == actual_locations


@pytest.mark.django_db
def test_list_options_for_location_exclude_blank():
    G(Item, location='', n=2)
    G(Item, location='Brighton', n=2)
    G(Item, location='London')
    expected_locations = ['Brighton', 'London']
    actual_locations = list(list_options('location'))
    assert expected_locations == actual_locations


@pytest.mark.django_db
def test_list_options_for_enumerator_retrieved_all_options():
    items = G(Item, n=5)
    expected_enumerators = [an_item.enumerator for an_item in items]
    actual_enumerators = list(list_options('enumerator'))
    assert expected_enumerators == actual_enumerators


@pytest.mark.django_db
def test_list_options_for_enumerator_unique():
    G(Item, enumerator='Rojina Akter', n=2)
    G(Item, enumerator='Nur Ankis', n=2)
    G(Item, enumerator='Rashada')
    expected_enumerators = ['Nur Ankis', 'Rashada', 'Rojina Akter', ]
    actual_enumerators = list(list_options('enumerator'))
    assert expected_enumerators == actual_enumerators


@pytest.mark.django_db
def test_list_options_for_enumerator_exclude_blank():
    items = G(Item, enumerator='', n=2)
    items.extend(G(Item, enumerator='Nur Ankis', n=2))
    items.append(G(Item, enumerator='Rashada'))
    expected_enumerators = ['Nur Ankis', 'Rashada']
    actual_enumerators = list(list_options('enumerator'))
    assert expected_enumerators == actual_enumerators


@pytest.mark.django_db
def test_list_options_for_collection_type_retrieved_all_options():
    items = G(Item, n=5)
    expected_collection_types = [an_item.collection_type for an_item in items]
    actual_collection_types = list(list_options('collection_type'))
    assert expected_collection_types == actual_collection_types


@pytest.mark.django_db
def test_list_options_for_collection_type_unique():
    G(Item, collection_type='Rojina Akter', n=2)
    G(Item, collection_type='Nur Ankis', n=2)
    G(Item, collection_type='Rashada')
    expected_collection_types = ['Nur Ankis', 'Rashada', 'Rojina Akter']
    actual_collection_types = list(list_options('collection_type'))
    assert expected_collection_types == actual_collection_types


@pytest.mark.django_db
def test_list_options_for_collection_type_exclude_blank():
    items = G(Item, collection_type='', n=2)
    items.extend(G(Item, collection_type='Nur Ankis', n=2))
    items.append(G(Item, collection_type='Rashada'))
    expected_collection_types = ['Nur Ankis', 'Rashada']
    actual_collection_types = list(list_options('collection_type'))
    assert expected_collection_types == actual_collection_types
