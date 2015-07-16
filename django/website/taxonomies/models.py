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
        db_index=True,  # Should be true by implication
        # https://docs.djangoproject.com/en/1.8/ref/models/fields/#slugfield
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Taxonomy, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

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


class TermManager(models.Manager):

    def by_taxonomy(self, taxonomy, name):
        """ Fetch an existing  Term by its name and its
        Taxonomy slug which, together should be unique together.

        args:
            taxonomy: [Taxonomy|string]
                Taxonomy instance or taxonomy slug.

            name: string: the name of an existing term

        returns:
            The term object with the given name in the given Taxonomy.

        throws:
            DoesNotExist if no Term matches the given combination
            ValueError if taxonomy is not one of the allowed types
        """
        if isinstance(taxonomy, basestring):
            taxonomy_slug = taxonomy
        elif isinstance(taxonomy, Taxonomy):
            taxonomy_slug = taxonomy.slug
        else:
            raise ValueError(
                "taxonomy must be a Taxonomy instance "
                "or a valid taxonomy slug")
        return self.get(taxonomy__slug=taxonomy_slug, name=name)


class Term(models.Model):

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=250,
        help_text=_('Tag or Category Name'),
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

    def __unicode__(self):
        return "{}:{}".format(
            self.taxonomy.name,
            self.name
        )

    # Custom Manager
    objects = TermManager()

    class Meta:
        unique_together = ('name', 'taxonomy')
        index_together = ['name', 'taxonomy']
