from datetime import timedelta

from django.utils import timezone

from factory.django import DjangoModelFactory
from factory import fuzzy

from data_layer.models import Item


class ItemFactory(DjangoModelFactory):

    class Meta:
        model = Item

    body = fuzzy.FuzzyText()
    timestamp = fuzzy.FuzzyDateTime(
        timezone.now() + timedelta(days=-365)
    )
