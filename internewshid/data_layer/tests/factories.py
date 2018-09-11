from datetime import timedelta

from django.utils import timezone

from factory import fuzzy
from factory.django import DjangoModelFactory

from data_layer.models import Item


class ItemFactory(DjangoModelFactory):

    class Meta:
        model = Item

    body = fuzzy.FuzzyText()
    timestamp = fuzzy.FuzzyDateTime(
        timezone.now() + timedelta(days=-365)
    )
