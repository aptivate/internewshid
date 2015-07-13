from __future__ import unicode_literals, absolute_import
from rest_framework import serializers

from data_layer.models import (
    Item,
    Taxonomy,
)


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item


class TaxonomySerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxonomy
