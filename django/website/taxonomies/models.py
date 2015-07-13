from django.db import models
from django.utils.translation import ugettext_lazy as _


class Taxonomy(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(
        _('Name'),
        max_length=250,
        help_text=_('Taxonomy Name'),
        unique=True,
        db_index=True,
    )

    # My thoughts on how this grows...
    #
    # multiplicity = models.CharField(
    #   ...
    #   choices=(
    #     ('optional', _('Zero or One')),
    #     ('multiple', _('Zero or More')),
    #   )
    # )
    #
    # vocabulary = models.CharField(
    #   ...
    #   choices=(
    #      ('fixed', _('Not modifiable by any user, system only')),
    #      ('closed', _('Only admin users who have permission to define and edit taxonomies')),
    #      ('open', _('Any user who has permission to use taxonomies')),
    #   )
    # )

    # To do Categories, you use 'optional' and 'closed',
    # to do free tagging use 'multiple' and 'open'



class Term(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(
        _('Name'),
        max_length=250,
        help_text=_('Taxonomy Name'),
        unique=True,
        db_index=True,
    )

    taxonomy = models.ForeignKey(
        Taxonomy,
        verbose_name=_('Taxonomy'),
        related_name="%(app_label)s_%(class)s_term"
    )

    long_name = models.TextField(
        verbose_name=_('Long Name'),
        blank=True,
    )
