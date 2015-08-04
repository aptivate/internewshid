from django.contrib import admin
from .models import TabbedPage, Tab


class TabInline(admin.StackedInline):
    model = Tab
    extra = 0


class TabbedPageAdmin(admin.ModelAdmin):
    inlines = [TabInline]


admin.site.register(TabbedPage, TabbedPageAdmin)
