import pytest

from taxonomies.tests.factories import TaxonomyFactory, TermFactory

from ..importer import Importer

COLUMN_LIST = [
    {
        'name': 'Province',
        'type': 'location',
        'field': 'message.location',
    },
    {
        'name': 'Message',
        'type': 'text',
        'field': 'message.content',
    },
]


@pytest.fixture
def importer():
    importer = Importer()

    importer.profile = {
        'columns': [d.copy() for d in COLUMN_LIST]
    }

    return importer


@pytest.fixture
def taxonomies():
    taxonomy_names = (
        'Item Types', 'Tags', 'Data Origins', 'Countries', 'Contexts',
        'Bangladesh Refugee Crisis Sectors', 'Age Ranges', 'Covid19 Theme'
    )
    taxonomies = {name: TaxonomyFactory(name=name) for name in taxonomy_names}

    term_keywords = [
        {
            'long_name': "Concern",
            'name': "concern",
            'taxonomy': taxonomies['Item Types'],
        },
        {
            'long_name': 'Question',
            'name': 'question',
            'taxonomy': taxonomies['Item Types'],
        },
        {
            'long_name': 'Rumour',
            'name': 'rumour',
            'taxonomy': taxonomies['Item Types'],
        },
        {
            'long_name': 'Geopoll Spreadsheet',
            'name': 'Geopoll Spreadsheet',
            'taxonomy': taxonomies['Data Origins'],
        },
        {
          'long_name': 'Rapidpro Spreadsheet',
          'name': 'Rapidpro Spreadsheet',
          'taxonomy': taxonomies['Data Origins'],
        },
        {
          'long_name': 'Form Entry',
          'name': 'Form Entry',
          'taxonomy': taxonomies['Data Origins'],
        },
        {
            'long_name': 'Liberia',
            'name': 'Liberia',
            'taxonomy': taxonomies['Countries'],
        },
        {
            'long_name': 'Ebola-Liberia',
            'name': 'Ebola-Liberia',
            'taxonomy': taxonomies['Contexts'],
        },
        {
            'long_name': 'WASH',
            'name': 'WASH',
            'taxonomy': taxonomies['Bangladesh Refugee Crisis Sectors'],
        },
        {
            'long_name': 'NFI / Shelter',
            'name': 'NFI / Shelter',
            'taxonomy': taxonomies['Bangladesh Refugee Crisis Sectors'],
        },
        {
            'long_name': 'Health',
            'name': 'Health',
            'taxonomy': taxonomies['Bangladesh Refugee Crisis Sectors'],
        },
        {
            'long_name': 'Education',
            'name': 'Education',
            'taxonomy': taxonomies['Bangladesh Refugee Crisis Sectors'],
        },
        {
            'long_name': 'Nutrition',
            'name': 'Nutrition',
            'taxonomy': taxonomies['Bangladesh Refugee Crisis Sectors'],
        },
        {
            'long_name': 'Child Protection',
            'name': 'Child Protection',
            'taxonomy': taxonomies['Bangladesh Refugee Crisis Sectors'],
        },
        {
            'long_name': 'Food Security',
            'name': 'Food Security',
            'taxonomy': taxonomies['Bangladesh Refugee Crisis Sectors'],
        },
        {
            'long_name': 'GBV',
            'name': 'GBV',
            'taxonomy': taxonomies['Bangladesh Refugee Crisis Sectors'],
        },
        {
            'long_name': 'Site Management',
            'name': 'Site Management',
            'taxonomy': taxonomies['Bangladesh Refugee Crisis Sectors'],
        },
        {
            'long_name': 'Protection',
            'name': 'Protection',
            'taxonomy': taxonomies['Bangladesh Refugee Crisis Sectors'],
        },
        {
            'name': 'Under 10 yrs',
            'long_name': 'Under 10 yrs',
            'taxonomy': taxonomies['Age Ranges'],
        },
        {
            'name': 'Age 11-14 yrs',
            'long_name': 'Age 11-14 yrs',
            'taxonomy': taxonomies['Age Ranges'],
        },
        {
            'name': 'Age 15-18 yrs',
            'long_name': 'Age 15-18 yrs',
            'taxonomy': taxonomies['Age Ranges'],
        },
        {
            'name': 'Age 19-25',
            'long_name': 'Age 19-25',
            'taxonomy': taxonomies['Age Ranges'],
        },
        {
            'name': 'Age 26-35',
            'long_name': 'Age 26-35',
            'taxonomy': taxonomies['Age Ranges'],
        },
        {
            'name': 'Age 36-45',
            'long_name': 'Age 36-45',
            'taxonomy': taxonomies['Age Ranges'],
        },
        {
            'name': 'Age 46-60',
            'long_name': "Age 46-60",
            'taxonomy': taxonomies['Age Ranges'],
        },
        {
            'name': "Over 60 years old",
            'long_name': "Over 60 years old",
            'taxonomy': taxonomies['Age Ranges'],
        }
    ]
    [TermFactory(**keywords) for keywords in term_keywords]
