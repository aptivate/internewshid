""" Handle the assets for the project so we can compile all
    javascript and css in a single file, which is the optimum
    way of building the resources for high latency and low
    bandwidth setups.

    The list of assets is not dynamic - to be built for production
    the list of assets in _assets must be defined in this file.

    Asset type is determined by file extension:
        .js: Javascript file
        .css: Css file
        .less: Less file

    To ensure dependencies are included, and to clearly express
    which components require certain css or javascript files,
    views may call 'require_assets' which will raise an
    AssetMissing exception if the given asset is not included
    statically here.
"""
from contextlib import contextmanager

from django_assets import Bundle, register

_assets = [
    # Stylesheets
    'less/internews-setup.less',
    'fonts/fontello/css/fontello.css',
    'dashboard/dashboard.css',

    # Javascript librairies
    'js/jquery.min.js',
    'bootstrap/js/bootstrap.min.js',
    'js/underscore.js',
    'js/backbone.js',
    'flot/jquery.flot.js',
    'flot/jquery.flot.resize.js',
    'hid/widgets/chart.js',
    'hid/js/spinner.js',
    'hid/js/automatic_file_upload.js',
    'hid/js/enable_multiselect.js',
    'js/bootstrap-multiselect.js',
    'js/bootstrap-tagsinput.js',
    'hid/js/select_all_checkbox.js',
    'hid/js/colResizable-1.6.js',
]


class AssetMissing(Exception):
    """ Exception raised when an asset is missing """
    pass


def require_assets(*assets):
    """ Ensure the given assets are included in the page's assets

    Args:
        assets: List of assets
    Raises:
        AssetMissing: If any of the asset is missing
    """
    global _assets
    for asset in assets:
        if asset not in _assets:
            raise AssetMissing("Missing asset: {0}".format(asset))


@contextmanager
def use_assets(*assets):
    """ Context manager to temporarily override the asset list.

    This is used for testing purposes only - assets not defined
    statically here will not be included in production
    environment.
    """
    global _assets
    old_assets = _assets
    try:
        _assets = assets
        yield
    finally:
        _assets = old_assets


register('javascript_assets', Bundle(
    *[a for a in _assets if a.endswith('.js')],
    filters='jsmin', output='js/javascript_assets.js'
))
register('css_assets', Bundle(
    *[a for a in _assets if a.endswith('.css') or a.endswith('.less')],
    filters='less, cssmin', output='css/css_assets.css',
    depends=['less/*.less']
))
