from django.conf import settings
from django.http import HttpResponse


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


class VirtualHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        set_urlconf = virtual_hosts.get(host)
        request.urlconf = set_urlconf
        if request.method == "OPTIONS":
            response = HttpResponse(status=204)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET,PUT,POST,DELETE"
            response["Vary"] = "Access-Control-Request-Headers"
            response["Access-Control-Allow-Headers"] = "authorization"
            return response
        else:
            '''
            if request.method == "PUT":
                request.method = "POST"
            '''
            response = self.get_response(request)
            if set_urlconf == "api.urls":
                response["Content-Type"] = "application/json; charset=utf-8"
                response["Access-Control-Allow-Origin"] = "*"
            return response