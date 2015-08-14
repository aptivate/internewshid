from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


def csrf_failure(request, reason=''):
    # If the user presses the back button in the browser to go back to the
    # login page and logs in again, they will get a CSRF error page because
    # the token will be wrong.
    # We override this with a redirect to the dashboard, which if not already
    # logged in, will redirect to the login page (with a fresh token).

    return HttpResponseRedirect(reverse('dashboard'))
