from django.contrib import admin

from .models import Item


class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'age',
        'body',
        'gender',
        'timestamp',
        'translation',
    )


admin.site.register(Item, ItemAdmin)
