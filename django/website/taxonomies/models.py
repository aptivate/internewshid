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
    # modifyable_by = models.CharField(
    #   ...
    #   choices=(
    #      ('system', _('Not modifyable by any user')),
    #      ('admin', _('Only users who have permission to definen taxonomies')),
    #      ('user', _('Any user who has permission to use taxonomies')),
    #   )
    # )

    # To do Categories or limited vocabularies, you use 'optional' and 'admin',
    # to do free taggingn use 'multiple' and 'user'



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
