from django.db import models
from django.dispatch.dispatcher import receiver

from taxonomies.models import Term
from taxonomies.exceptions import TermException


class DataLayerModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def note_external_modification(self):
        # This will set the last_modified field
        self.save()


class Message(DataLayerModel):
    body = models.TextField()
    timestamp = models.DateTimeField(null=True)
    terms = models.ManyToManyField(Term, related_name="items")
    network_provider = models.CharField(max_length=200, blank=True)

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
            raise TermException("Terms cannot be applied from different taxonomies")

        if not taxonomy.is_multiple:
            if len(terms) > 1:
                message = "Taxonomy '%s' does not support multiple terms" % taxonomy
                raise TermException(message)

            self.delete_all_terms(taxonomy)

        self.terms.add(*terms)

    def delete_all_terms(self, taxonomy):
        for term in self.terms.filter(taxonomy=taxonomy):
            self.terms.remove(term)

    def __unicode__(self):
        return "{}: '{}' @{}".format(
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
