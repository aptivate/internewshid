from django.contrib import admin

from .models import Item


class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'body',
        'translation',
        'timestamp',
    )


admin.site.register(Item, ItemAdmin)
