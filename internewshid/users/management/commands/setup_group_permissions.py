from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import CommandError, NoArgsCommand

from contacts.group_permissions import GroupPermissions


class Command(NoArgsCommand):
    help = """Sets up groups and their associated permissions.
    See group_permissions.py"""

    def handle_noargs(self, **options):
        verbose = int(options.get('verbosity', 1)) > 1
        try:
            GroupPermissions(verbose=verbose).setup_groups_and_permissions()
        except ObjectDoesNotExist as e:
            raise CommandError(e.message)
