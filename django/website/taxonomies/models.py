from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


class Taxonomy(models.Model):

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=250,
        help_text=_('Taxonomy Name'),
        unique=True,
        db_index=True,
    )
    slug = models.SlugField(
        verbose_name=_('Slug'),
        max_length=250,
        unique=True,  # Should be true already
        db_index=True,  #  Should be true by implication
        # https://docs.djangoproject.com/en/1.8/ref/models/fields/#slugfield
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Taxonomy, self).save(*args, **kwargs)

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

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=250,
        help_text=_('Tag or Category Name'),
        unique=True,
        db_index=True,
    )

    taxonomy = models.ForeignKey(
        'taxonomies.Taxonomy',
        verbose_name=_('Taxonomy'),
        related_name="%(app_label)s_%(class)s_term"
    )

    long_name = models.TextField(
        verbose_name=_('Long Name'),
        blank=True,
    )
