from django.test import TestCase

from hid.assets import AssetMissing, require_assets, use_assets


class TestAssets(TestCase):
    def test_requiring_existing_assets_does_not_raise(self):
        with use_assets('a.css', 'b.css', 'c.js'):
            try:
                require_assets('a.css', 'c.js')
            except AssetMissing:
                raise
                self.fail('AssetMissing raised unexpectedly')

    def test_requiring_missing_assets_does_raise(self):
        with use_assets('a.css', 'b.css', 'c.js'):
            with self.assertRaises(AssetMissing):
                require_assets('a.css', 'missing.js')
