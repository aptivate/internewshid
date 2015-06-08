from __future__ import unicode_literals, absolute_import

import collections
from urlparse import urlsplit

from django.core.urlresolvers import resolve, reverse
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.core.files import File

class FakeSession(collections.MutableMapping):
    """
    http://stackoverflow.com/questions/3387691/python-how-to-perfectly-override-a-dict
    """

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def set_test_cookie(self):
        pass

class FastDispatchMixin(object):

    default_cms_page = None

    def get_fake_request(self, path, method='get', get_params=None, 
        post_params=None, request_extras=None, file_params=None):

        get_params  = get_params  if get_params  else {}
        post_params = post_params if post_params else {}
        file_params = file_params if file_params else {}

        factory = RequestFactory()
        handler = getattr(factory, method)
        request = handler(path, post_params)

        request.GET = request.GET.copy()
        for key, value in get_params.iteritems():
            if hasattr(value, '__iter__'):
                request.GET.setlist(key, value)
            else:
                if not isinstance(value, basestring):
                    raise Exception("GET and POST can only contain strings, "
                        "but %s = %s (%s)" % (key, value, value.__class__))
                request.GET.setlist(key, [value])

        request.POST = request.POST.copy()
        for key, value in post_params.iteritems():
            if isinstance(value, File):
                request.FILES.setlist(key, [value])
            elif hasattr(value, '__iter__'):
                request.POST.setlist(key, value)
            else:
                if not isinstance(value, basestring):
                    raise Exception("GET and POST can only contain strings, "
                        "but %s = %s (%s)" % (key, value, value.__class__))
                request.POST.setlist(key, [value])

        for key, value in file_params.iteritems():
            request.FILES.setlist(key, [value])

        # Make them immutable to catch abuses that otherwise would only
        # appear in real life, not in the tests.
        request.GET._mutable = False
        request.POST._mutable = False

        request.session = FakeSession()
        request._messages = FallbackStorage(request)

        from django.conf import settings

        if 'django.contrib.auth.middleware.AuthenticationMiddleware' in settings.MIDDLEWARE_CLASSES:
            from django.contrib.auth.models import AnonymousUser
            request.user = getattr(self, 'user', AnonymousUser())

        if 'django.middleware.locale.LocaleMiddleware' in settings.MIDDLEWARE_CLASSES:
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE

        # Resources filter plugin tests use this a lot.
        request.current_page = self.default_cms_page

        self.request_hook(request)

        if request_extras is not None:
            for key, value in request_extras.iteritems():
                setattr(request, key, value)

        return request

    def fast_dispatch(self, view_name, method='get', url_args=None, 
        url_kwargs=None, post_params=None, get_params=None, language=None,
        request_extras=None, file_params=None):

        url_args    = url_args    if url_args    else []
        url_kwargs  = url_kwargs  if url_kwargs  else {}

        from django.utils.translation import override
        with override(language):
            path = reverse(view_name, args=url_args, kwargs=url_kwargs)
            resolved = resolve(path)

            view = resolved.func
            view.request = self.get_fake_request(path, method, get_params,
                post_params, request_extras, file_params)
            self.last_request = view.request
            response = view(view.request, *resolved.args, **resolved.kwargs)
            response.view = view

            # make sure that we render while language override is in effect!
            if language is not None and hasattr(response, 'render'):
                response.render()

        return response

    def request_hook(self, request):
        pass

    def assertRedirectsNoFollow(self, response, expected_url):
        self.assertTrue(response._headers['location'][1].endswith(expected_url))
        self.assertEqual(response.status_code, 302)

    def assert_not_redirected(self, response, expected_status_code=200,
        msg_prefix=''):

        if msg_prefix:
            msg_prefix += ": "

        try:
            location = response._headers['location'][1]
            msg_prefix += ("unexpectedly redirected to %s" % location)
        except KeyError:
            # no location header
            pass

        self.assertEqual(response.status_code, expected_status_code,
            msg_prefix)

    def assert_no_adminform_with_errors(self, response):
        if not hasattr(response, 'context'):
            return

        adminform = self.assertInDict('adminform', response.context)

        if not adminform:
            return

        # if there are global errors, this will fail, and show us all
        # the errors when it does.
        self.assertDictEqual({}, adminform.form.errors)

        # if there are field errors, this will fail, and show us the
        # the field name and the errors
        for fieldset in adminform:
            for line in fieldset:
                # should this be line.errors()?
                # as FieldlineWithCustomReadOnlyField.errors
                # is a method, not a property:
                self.assertIsNone(line.errors,
                    "should not be any errors on %s" % line)
                for field in line:
                    # similarly django.contrib.admin.helpers.AdminField.errors
                    # is a method:
                    self.assertIsNone(field.errors,
                        "should not be any errors on %s" % field)

        self.assertIsNone(adminform.form.non_field_errors)

    def assert_redirected_mini(self, response, expected_url, status_code=302,
            host=None, msg_prefix=''):
        """
        Without trying to retrieve the redirect target URL, so it works with
        fast_dispatch.
        """

        if msg_prefix:
            msg_prefix += ": "

        if 'content' in dir(response):
            if hasattr(response, 'render'):
                response.render()

            if isinstance(response.content, str):
                content = unicode(response.content, 'utf-8')
            else:
                content = response.content

            msg_prefix = content + u"\n\n" + unicode(msg_prefix)

        self.assertEqual(response.status_code, status_code,
            msg_prefix + "Response didn't redirect as expected: Response"
            " code was %d (expected %d)" % (response.status_code, status_code))

        actual_url = response['Location']
        scheme, netloc, path, query, fragment = urlsplit(actual_url)

        # Redirect URLs are canonicalised by middleware that we've bypassed,
        # so we're expecting a path, not a URL, for local redirects.
        """
        e_scheme, e_netloc, e_path, e_query, e_fragment = urlsplit(expected_url)
        if not (e_scheme or e_netloc):
            expected_url = urlunsplit(('http', host or 'testserver', e_path,
                e_query, e_fragment))
        """

        self.assertEqual(actual_url, expected_url,
            msg_prefix + "Response redirected to '%s', expected '%s'" %
                (actual_url, expected_url))

    def assert_login_required(self, view_name, message='', *args, **kwargs):
        response = self.fast_dispatch(view_name, *args, **kwargs)

        from django.core.urlresolvers import reverse
        uri = reverse(view_name, args=kwargs.get('url_args', []),
           kwargs=kwargs.get('url_kwargs', {}))

        from django.conf import settings
        login_url = settings.LOGIN_URL + "?next=" + uri
        self.assert_redirected_mini(response, login_url, msg_prefix=message)

        return response

    def stuff_session(self, dictionary):
        from django.conf import settings
        if settings.SESSION_ENGINE != 'django.contrib.sessions.backends.db':
            print "Unknown session engine: %s Sessions won't work" % settings.SESSION_ENGINE
            return
        self.client.logout()
        from django.contrib.sessions.backends.db import SessionStore
        store = SessionStore()
        store.save()  # we need to make load() work, or the cookie is worthless
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key
        self.client.session.update(dictionary)
        self.client.session.save()
        self.client.login(username=self.user.username, password=self.password)

    def assertInDict(self, member, container, msg=None):
        """
        Returns the member if the assertion passes.

        Makes sense that if you're asserting that a dictionary has a
        member, you might want to use that member! Just saying. If not,
        you can always throw it away.
        """

        self.assertIn('__getitem__', dir(container), "Only use this assertion "
            "with a dict as the container")
        self.assertIn(member, container, msg=msg)

        try:
            return container[member]
        except TypeError as e:
            raise TypeError(("%s (is the second argument really a " +
                "dictionary? %s)") % (e, container))

    def assertContains(self, response, text, count=None, status_code=200,
                       msg_prefix='', html=False):
        if msg_prefix:
            msg_prefix = msg_prefix + ': '

        if hasattr(response, 'render'):
            response.render()

        from django.utils.encoding import force_text
        content = force_text(response.content)
        msg_prefix = content + "\n\n" + msg_prefix

        try:
            super(FastDispatchMixin, self).assertContains(response, text,
                count, status_code, msg_prefix, html)
        except AssertionError as e:
            import sys
            raise sys.exc_info()[0], "%s\n\nThe complete response was:\n%s" % \
                (e, content), sys.exc_info()[2]

    def absolute_url_for_site(self, relative_url):
        """
        Convert a relative URL to an absolute URL, using the name of the
        current site, which is hackish but doesn't require a request object
        (so it can be generated in an email, for example), makes the
        canonical name configurable, and matches what the absurl
        templatetag does.
        """

        from django.contrib.sites.models import Site
        return "http://%s%s" % (Site.objects.get_current().domain,
            relative_url)

    def absolute_url_for_request(self, relative_url):
        """
        Convert a relative URL to an absolute URL, using the server name
        hard-coded in django.test.client.RequestFactory, which matches the
        value used by HttpRequest.build_absolute_uri when called by
        the test client.
        """

        return "http://%s%s" % ('testserver', relative_url)

