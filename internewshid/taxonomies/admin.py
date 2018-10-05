from django.contrib import admin

from .models import Taxonomy, Term

admin.site.register(Taxonomy, admin.ModelAdmin)
admin.site.register(Term, admin.ModelAdmin)
