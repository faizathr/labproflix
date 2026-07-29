from django.conf import settings


def api_host(request):
    """Expose the API base URL to templates.

    The API and the backend are served by the same process on the same port
    (see labpro/hosts.py), so only the hostname differs. Deriving the value
    per request keeps the frontend working across local, staging and
    production without a hardcoded host in the JavaScript.
    """
    host = request.get_host()
    # Take the port from the Host header, not request.get_port(): behind a port
    # mapping or a proxy, SERVER_PORT is the internal port (80) rather than the
    # one the browser actually connected to.
    port = host.partition(":")[2]
    hostname = settings.API_HOSTS[0] if settings.API_HOSTS else host.partition(":")[0]
    netloc = "{}:{}".format(hostname, port) if port else hostname
    return {"API_HOST": "{}://{}".format(request.scheme, netloc)}
