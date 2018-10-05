from django.contrib import admin

from .models import SheetProfile

admin.site.register(SheetProfile, admin.ModelAdmin)
