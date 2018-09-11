from django.contrib import admin

from .models import TabbedPage, TabInstance


class TabInline(admin.StackedInline):
    model = TabInstance
    extra = 0


class TabbedPageAdmin(admin.ModelAdmin):
    inlines = [TabInline]


admin.site.register(TabbedPage, TabbedPageAdmin)
