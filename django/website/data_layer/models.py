from django.db import models
from taxonomies.models import Term


class DataLayerModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


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
