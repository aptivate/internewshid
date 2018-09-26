from django.contrib import admin
from .models import Term, Taxonomy

admin.site.register(Taxonomy, admin.ModelAdmin)
admin.site.register(Term, admin.ModelAdmin)
