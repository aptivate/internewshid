from __future__ import unicode_literals, absolute_import
from rest_framework import serializers

from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
