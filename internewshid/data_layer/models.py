from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _

from constance.backends.database import DatabaseBackend

from taxonomies.exceptions import TermException
from taxonomies.models import Term

try:
    from picklefield import PickledObjectField
except ImportError:
    raise ImproperlyConfigured('Could not import django-picklefield.')


class DataLayerModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def note_external_modification(self):
        # This will set the last_modified field
        self.save()


class Message(DataLayerModel):

    class Meta:
        permissions = (
            ('can_change_message_body', 'Can change feedback'),
        )

    # FIXME(lukem): We're thinking that this can be named 'source' or
    # `original` or something like that since it more closely resembles our
    # current thinking and since we're adding the new `translation` field,
    # we're pretty sure `body` is not the right name now. Leaving this here as
    # something to deal with when we get further into work.
    body = models.TextField(blank=True)
    translation = models.TextField(blank=True)
    timestamp = models.DateTimeField(null=True)
    terms = models.ManyToManyField(Term, related_name="items")
    network_provider = models.CharField(max_length=190, blank=True)
    location = models.CharField(max_length=100, blank=True)
    sub_location = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=190, blank=True)
    risk = models.CharField(max_length=30, blank=True)
    gender = models.CharField(max_length=100, blank=True)
    age = models.CharField(max_length=100, blank=True)
    contributor = models.CharField(max_length=190, blank=True)
    collection_type = models.CharField(max_length=190, blank=True)
    external_id = models.CharField(max_length=80, blank=True)

    def apply_terms(self, terms):
        """ Add or replace values of term.taxonomy for current Item

        For taxonomies that support multiple terms eg tags, do not remove any
        existing terms.

        IF the taxonomy is optional eg categories, and the Item has a term in
        that taxonomy already, replace it
        """
        # It bugs me that so much of the logic applying to taxonomies is here.
        # This should really be built out with an explicity through model
        # in taxonomies, with a generic foreign ken to the content type
        # being classified, then this logic could live there.
        if isinstance(terms, Term):
            terms = [terms]

        taxonomy = terms[0].taxonomy

        if not all(t.taxonomy == taxonomy for t in terms):
            raise TermException(_("Terms cannot be applied from different taxonomies"))

        if not taxonomy.is_multiple:
            if len(terms) > 1:
                message = _("Taxonomy '{0}' does not support multiple terms").format(taxonomy)
                raise TermException(message)

            self.delete_all_terms(taxonomy)

        self.terms.add(*terms)

    def delete_all_terms(self, taxonomy):
        for term in self.terms.filter(taxonomy=taxonomy):
            self.terms.remove(term)

    def __str__(self):
        return u"{0}: '{1}' @{2}".format(
            self.id,
            self.body,
            self.timestamp
        )


# TODO: rename this class
Item = Message


@receiver(models.signals.m2m_changed, sender=Item.terms.through,
          dispatch_uid="data_layer.models.terms_signal_handler")
def terms_signal_handler(sender, **kwargs):
    if kwargs.get('action') not in ('post_add', 'post_remove'):
        return

    if kwargs.get('reverse'):
        items = Item.objects.filter(pk__in=kwargs.get('pk_set'))
    else:
        items = [kwargs.get('instance')]

    for item in items:
        item.note_external_modification()


class CustomConstance(models.Model):
    key = models.CharField(max_length=190, unique=True)
    value = PickledObjectField()

    class Meta:
        managed = False
        verbose_name = _('constance')
        verbose_name_plural = _('constances')
        db_table = 'constance_config'

    def __str__(self):
        return self.key


class CustomConstanceBackend(DatabaseBackend):

    def __init__(self, *args, **kwargs):
        super(CustomConstanceBackend, self).__init__(*args, **kwargs)
        self._model = CustomConstance
