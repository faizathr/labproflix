from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers


def _build_virtual_hosts():
    """Map each configured hostname to its urlconf, with and without a port."""
    hosts = {}
    for urlconf, names in (
        ("be.urls", settings.BACKEND_HOSTS),
        ("api.urls", settings.API_HOSTS),
    ):
        for name in names:
            hosts[name] = urlconf
            if ":" not in name:
                for port in settings.VIRTUAL_HOST_PORTS:
                    hosts["{}:{}".format(name, port)] = urlconf
    return hosts


virtual_hosts = _build_virtual_hosts()


def _allow_origin(request, response):
    """Grant this request's Origin cross-origin access, if it has any.

    An empty CORS_ALLOWED_ORIGINS keeps the blanket wildcard the api host has
    always sent. Once the setting names origins the header has to echo the
    caller back one at a time, which makes the response depend on Origin — so
    caches are told not to serve one origin's copy to another.
    """
    allowed = settings.CORS_ALLOWED_ORIGINS
    if not allowed:
        response["Access-Control-Allow-Origin"] = "*"
        return
    patch_vary_headers(response, ["Origin"])
    origin = request.headers.get("Origin")
    if origin in allowed:
        response["Access-Control-Allow-Origin"] = origin


class VirtualHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        set_urlconf = virtual_hosts.get(host)
        request.urlconf = set_urlconf
        if request.method == "OPTIONS":
            response = HttpResponse(status=204)
            response["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE"
            patch_vary_headers(response, ["Access-Control-Request-Headers"])
            # Echo whatever the browser asked to send. Naming only
            # "authorization" here blocked every JSON request, because the
            # Content-Type a fetch body sets is itself a preflighted header.
            response["Access-Control-Allow-Headers"] = request.headers.get(
                "Access-Control-Request-Headers", "authorization,content-type"
            )
            _allow_origin(request, response)
            return response
        else:
            '''
            if request.method == "PUT":
                request.method = "POST"
            '''
            response = self.get_response(request)
            if set_urlconf == "api.urls":
                response["Content-Type"] = "application/json; charset=utf-8"
                _allow_origin(request, response)
            return response