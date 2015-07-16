from __future__ import unicode_literals, absolute_import
from rest_framework import serializers

from data_layer.models import Item

from taxonomies.models import (
    Taxonomy,
    Term,
)


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item


class TaxonomySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(
        required=False,
        # FIXME: max_length=250, causes AppRegistryNotReady excpetion!" Go figure
    )

    class Meta:
        model = Taxonomy


class TermSerializer(serializers.ModelSerializer):
    taxonomy = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Taxonomy.objects.all()
    )

    class Meta:
        model = Term
