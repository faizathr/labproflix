from django.http import HttpResponse

virtual_hosts = {
    "api.labpro.local:8000": "api.urls",
    "labpro.local:8000": "be.urls",
    "api.labpro.local": "api.urls",
    "labpro.local": "be.urls",
    "localhost:8000": "api.urls",
    "localhost": "api.urls",
}


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