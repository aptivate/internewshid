from django.db import models
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _


class Taxonomy(models.Model):

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=190,
        help_text=_('Taxonomy Name'),
        unique=True,
        db_index=True,
    )
    slug = models.SlugField(
        verbose_name=_('Slug'),
        max_length=190,
        unique=True,  # Should be true already
        db_index=True,  # Should be true by implication
        # https://docs.djangoproject.com/en/1.8/ref/models/fields/#slugfield
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Taxonomy, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    # To do Categories, you use 'optional' and 'closed',
    # to do free tagging use 'multiple' and 'open'
    multiplicity = models.CharField(
        choices=(
            ('optional', _('Zero or One')),
            ('multiple', _('Zero or More')),
        ),
        default='optional',
        max_length=30,
    )

    @property
    def is_optional(self):
        return self.multiplicity == 'optional'

    @property
    def is_multiple(self):
        return self.multiplicity == 'multiple'

    vocabulary = models.CharField(
        choices=(
            ('fixed', _('Not modifiable by any user, system only')),
            ('closed', _('Only admin users who have permission to define and edit taxonomies')),
            ('open', _('Any user who has permission to use taxonomies')),
        ),
        default='closed',
        max_length=30,
    )

    @property
    def is_open(self):
        return self.vocabulary == 'open'


class TermManager(models.Manager):

    def by_taxonomy(self, taxonomy, name):
        """ Fetch a Term by its name and its
        Taxonomy slug which, together should be unique together.

        args:
            taxonomy: [Taxonomy|string]
                Taxonomy instance or taxonomy slug.

            name: string: the name of an existing term

        returns:
            The term object with the given name in the given Taxonomy.

        throws:
            DoesNotExist if Taxonomy with the given slug does not exist
            DoesNotExist if named Term does not exist, unless the Taxonomy
            vocabulary is open - in this case the Term will be created
            ValueError if taxonomy is not one of the allowed types
        """
        if isinstance(taxonomy, basestring):
            taxonomy = Taxonomy.objects.get(slug=taxonomy)
        elif not isinstance(taxonomy, Taxonomy):
            raise ValueError(
                "taxonomy must be a Taxonomy instance "
                "or a valid taxonomy slug")

        if taxonomy.is_open:
            term, _ = self.select_related('taxonomy').get_or_create(
                taxonomy=taxonomy,
                name=name
            )
        else:
            term = self.select_related('taxonomy').get(
                taxonomy=taxonomy,
                name=name
            )

        return term


class Term(models.Model):

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=190,
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
        return u"{0}:{1}".format(
            self.taxonomy.name,
            self.name,
        )

    # Custom Manager
    objects = TermManager()

    class Meta:
        unique_together = ('name', 'taxonomy')
        index_together = ['name', 'taxonomy']
