from django.contrib import admin

from jsoneditor.forms import JSONEditor
from jsonfield import JSONField

from .models import SheetProfile


class SheetProfileAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': JSONEditor},
    }


admin.site.register(SheetProfile, SheetProfileAdmin)
