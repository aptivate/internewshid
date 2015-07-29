from django.db import models
from django.dispatch.dispatcher import receiver
from django.utils import timezone

from taxonomies.models import Term


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

    def apply_term(self, term):
        # TODO: test this
        """ Add or replace value of term.taxonomy for current Item

        If the Item has no term in the taxonomy
        OR if the taxonomy.is_multiple just add it.
        IF the taxonmy is optional (categories)
            If the Item has a term in that taxonomy already,
                replace it
        """
        # It bugs me that so much of the logic applying to taxonomies is here.
        # This should really be built out with an explicity through model
        # in taxonomies, with a generic foreign ken to the content type
        # being classified, then this logic could live there.
        if term.taxonomy.is_optional:
            for old_term in self.terms.filter(taxonomy=term.taxonomy):
                self.terms.remove(old_term)
        self.terms.add(term)

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
    if kwargs.get('action') == 'post_add':
        instance = kwargs.get('instance')
        instance.note_external_modification()
