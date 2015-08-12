from __future__ import unicode_literals, absolute_import
from rest_framework import serializers

from data_layer.models import Item

from taxonomies.models import (
    Taxonomy,
    Term,
)


class TaxonomySerializer(serializers.ModelSerializer):

    class Meta:
        model = Taxonomy

    slug = serializers.SlugField(
        required=False,
        # FIXME: max_length=250, causes AppRegistryNotReady excpetion!" Go figure
    )


class TermSerializer(serializers.ModelSerializer):

    class Meta:
        model = Term
        fields = ('taxonomy', 'name', 'long_name', )

    taxonomy = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Taxonomy.objects.all()
    )


class TermItemCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ('name', 'long_name', 'count', )

    count = serializers.IntegerField(
        read_only=True
    )


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item

    terms = TermSerializer(many=True)

    def create(self, validated_data):
        """ Create an item with nested metadata terms
        The validated data looks something like this:
        {   "body": "some text",
            "terms": [
                {"taxonomy": "animal", "name": "Dog"},
                {"taxonomy": "thing", "name": "foo"}
            ],
        }
        """
        # find all terms listed in term_data and link to item
        # in future, we might theoreteically be adding new tags here too,
        # in which case there will be more edge cases to detect
        # because you're only allowed to add if the taxonomy allows it
        # when we add that feature to taxonomies.
        term_list = validated_data.pop('terms', [])
        item = Item.objects.create(**validated_data)
        for term_data in term_list:
            term = Term.objects.by_taxonomy(
                taxonomy=term_data['taxonomy'],
                name=term_data['name'],
            )
            item.terms.add(term)
        return item

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
