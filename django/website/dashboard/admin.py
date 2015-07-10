from django.contrib import admin
from .models import Dashboard, WidgetInstance


class WidgetInstanceInline(admin.StackedInline):
    model = WidgetInstance
    extra = 0


class DashboardAdmin(admin.ModelAdmin):
    inlines = [WidgetInstanceInline]


admin.site.register(Dashboard, DashboardAdmin)
