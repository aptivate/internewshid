from __future__ import unicode_literals, absolute_import

from django.test.testcases import SimpleTestCase

from transport import data_layer_transport as dl


class TransportLayerMessageTests(SimpleTestCase):

    def test_get_messages_exists(self):
        models = dl.get_messages()
        self.assertEqual(len(models), 0)
