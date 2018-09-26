from django.contrib import admin
from .models import SheetProfile

# Register your models here.
admin.site.register(SheetProfile, admin.ModelAdmin)
