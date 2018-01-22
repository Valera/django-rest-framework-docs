from importlib import import_module
from django.conf import settings
from django.urls import URLPattern, URLResolver
# from django.core.urlresolvers import RegexURLResolver, RegexURLPattern
from django.urls.resolvers import RoutePattern, RegexPattern
from django.utils.module_loading import import_string
from rest_framework.views import APIView
from rest_framework_docs.api_endpoint import ApiEndpoint


class ApiDocumentation(object):

    def __init__(self, drf_router=None):
        self.endpoints = []
        self.drf_router = drf_router
        try:
            root_urlconf = import_string(settings.ROOT_URLCONF)
        except ImportError:
            # Handle a case when there's no dot in ROOT_URLCONF
            root_urlconf = import_module(settings.ROOT_URLCONF)
        if hasattr(root_urlconf, 'urls'):
            self.get_all_view_names(root_urlconf.urls.urlpatterns)
        else:
            self.get_all_view_names(root_urlconf.urlpatterns)

    def get_all_view_names(self, urlpatterns, parent_regex=''):
        for pattern in urlpatterns:
            if isinstance(pattern, URLResolver):
                if isinstance(pattern.pattern, RoutePattern):
                    regex = pattern.pattern._route
                elif isinstance(pattern.pattern, RegexPattern):
                    regex = pattern.pattern._regex
                # regex = '' if pattern.pattern is None or pattern.pattern == "^" else pattern.pattern
                self.get_all_view_names(urlpatterns=pattern.url_patterns, parent_regex=parent_regex + regex)
            elif isinstance(pattern, URLPattern) and self._is_drf_view(pattern) and not self._is_format_endpoint(pattern):
                if isinstance(pattern.pattern, RoutePattern):
                    regex = pattern.pattern._route
                elif isinstance(pattern.pattern, RegexPattern):
                    regex = pattern.pattern._regex

                api_endpoint = ApiEndpoint(pattern, parent_regex, self.drf_router)
                self.endpoints.append(api_endpoint)

    def _is_drf_view(self, pattern):
        """
        Should check whether a pattern inherits from DRF's APIView
        """
        return hasattr(pattern.callback, 'cls') and issubclass(pattern.callback.cls, APIView)

    def _is_format_endpoint(self, pattern):
        """
        Exclude endpoints with a "format" parameter
        """
        if isinstance(pattern.pattern, RoutePattern):
            regex = pattern.pattern._route
        elif isinstance(pattern.pattern, RegexPattern):
            regex = pattern.pattern._regex
        else:
            assert 0
        return '?P<format>' in regex

    def get_endpoints(self):
        return self.endpoints
