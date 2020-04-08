from django.contrib import admin

from jsoneditor.forms import JSONEditor
from jsonfield import JSONField

from .models import TabbedPage, TabInstance


class TabInline(admin.StackedInline):
    formfield_overrides = {
        JSONField: {'widget': JSONEditor},
    }

    model = TabInstance
    extra = 0


class TabbedPageAdmin(admin.ModelAdmin):
    inlines = [TabInline]


admin.site.register(TabbedPage, TabbedPageAdmin)
