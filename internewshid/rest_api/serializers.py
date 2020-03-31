from rest_framework import serializers, validators

from data_layer.models import Item, Value
from taxonomies.models import Taxonomy, Term

from .fields import IgnoreMicrosecondsDateTimeField


class TaxonomySerializer(serializers.ModelSerializer):

    class Meta:
        model = Taxonomy
        fields = (
            '__all__'
        )

    slug = serializers.SlugField(
        required=False,
        # FIXME: max_length=250, causes AppRegistryNotReady excpetion!" Go figure
    )


class TermSerializer(serializers.ModelSerializer):

    class Meta:
        model = Term
        fields = (
            'taxonomy',
            'name',
            'long_name',
        )

    taxonomy = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Taxonomy.objects.all()
    )


class TermItemCountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Term
        fields = (
            'name',
            'long_name',
            'count',
        )

    count = serializers.IntegerField(
        read_only=True
    )


class TermExportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Term
        fields = (
            'name',
        )

    def to_representation(self, instance):
        return instance.name


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = (
            '__all__'
        )
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Item.objects.all(),
                fields=('body', 'timestamp')
            )
        ]

    timestamp = IgnoreMicrosecondsDateTimeField()
    terms = TermSerializer(many=True, required=False)
    values = serializers.SerializerMethodField()

    def get_values(self, item):
        return {kv.key.key:kv.value for kv in item.values.all()}

    def create(self, validated_data):
        """ Create an item with nested metadata terms."""
        # find all terms listed in term_data and link to item
        # in future, we might theoreteically be adding new tags here too,
        # in which case there will be more edge cases to detect
        # because you're only allowed to add if the taxonomy allows it
        # when we add that feature to taxonomies.
        term_list = validated_data.pop('terms', [])
        item = Item.objects.create(**validated_data)

        # TODO: This doesn't seem to be used by transport layer
        # (terms always end up empty)
        for term_data in term_list:
            term = Term.objects.by_taxonomy(
                taxonomy=term_data['taxonomy'],
                name=term_data['name'],
            )
            item.terms.add(term)
        return item

    def update(self, item, validated_data):
        # TODO: Currently we don't do anything with terms
        validated_data.pop('terms', [])

        for attr, value in validated_data.items():
            setattr(item, attr, value)
        item.save()

        return item


class LocationCoverageSerializer(ItemSerializer):
    terms = TermExportSerializer(many=True)

    # https://github.com/wq/django-rest-pandas#date-formatting
    timestamp = serializers.DateField(format=None)

    class Meta:
        model = Item
        fields = (
            'location',
            'terms',
            'timestamp',
        )


class ItemExportSerializer(ItemSerializer):
    terms = TermExportSerializer(many=True)

    # https://github.com/wq/django-rest-pandas#date-formatting
    timestamp = serializers.DateField(format=None)

    class Meta:
        model = Item
        fields = (
            'age',
            'body',
            'collection_type',
            'contributor',
            'external_id',
            'gender',
            'location',
            'network_provider',
            'sub_location',
            'terms',
            'timestamp',
            'translation',
        )
