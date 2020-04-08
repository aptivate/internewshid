from django.contrib import admin

from jsoneditor.forms import JSONEditor
from jsonfield import JSONField

from .models import Dashboard, WidgetInstance


class WidgetInstanceInline(admin.StackedInline):
    formfield_overrides = {
        JSONField: {'widget': JSONEditor},
    }

    model = WidgetInstance
    extra = 0


class DashboardAdmin(admin.ModelAdmin):
    inlines = [WidgetInstanceInline]


admin.site.register(Dashboard, DashboardAdmin)
