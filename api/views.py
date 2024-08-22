from be.models import Profile, Film
from be.auth import JWT, AUTH

from django.http import HttpResponse, QueryDict
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from labpro.hosts import virtual_hosts

from . import urls
from .forms import CreateFilm

import datetime
import json
import jwt
import pytz
import uuid

class Data:
    def __init__(self, status=True, message="", data=None):
        self.data = {
            "status": "success" if status else "error",
            "message": message,
            "data": data
        }
    def get_json(self):
        return json.dumps(self.data, indent=4)

class ErrorPages:
    def Error400(message="Bad request", data=None):
        return HttpResponse(Data(False, message, data).get_json(), status=400)
    def Error401(message="Unauthorized", data=None):
        return HttpResponse(Data(False, message, data).get_json(), status=401)
    def Error405(message="Method not allowed", data=None):
        return HttpResponse(Data(False, message, data).get_json(), status=405)

def is_substr(str, substr):
    try:
        str.index(substr)
    except:
        return False
    return True

@csrf_exempt
def index(request):
    if request.method == "GET":
        return HttpResponse(Data(True, "Infrasture is up", {
            "api": {
                "url": list(virtual_hosts.keys())[list(virtual_hosts.values()).index("api.urls")],
            },
            "web": {
                "url": list(virtual_hosts.keys())[list(virtual_hosts.values()).index("be.urls")],
            }
        }).get_json())
    else:
        return ErrorPages.Error405()

@csrf_exempt
def films(request):
    if request.method == "GET":
        use_cached = False
        cached_data = ""
        cache_key = ""
        search_data = {}
        search_results = []
        if request.GET.get('q') and request.GET['q'] != "":
            cache_key = "search_films:{}".format(request.GET['q'])
            cached_data = cache.get(cache_key)
            if cached_data and cached_data != "":
                use_cached = True
            else:
                search_by_title = Film.objects.filter(title__icontains = request.GET['q'])
                search_by_director = Film.objects.filter(director__icontains = request.GET['q'])
                search_data = (search_by_title | search_by_director).distinct().order_by('-created_at')
        else:
            cache_key = "films"
            cached_data = cache.get(cache_key)
            if cached_data and cached_data != "":
                use_cached = True
            else:
                search_data = Film.objects.all().order_by('-created_at')
        if use_cached:
            search_results = json.loads(cached_data)
        else:
            for i in search_data:
                search_results.append({
                    "id": str(i.id),
                    "director": i.director,
                    "duration": i.duration,
                    "description": i.description,
                    "price": i.price,
                    "release_year": i.release_year,
                    "title": i.title,
                    "genre": json.loads(i.genre),
                    "created_at": i.created_at.isoformat()[:23]+"Z",
                    "updated_at": i.updated_at.isoformat()[:23]+"Z",
                    "cover_image_url": i.cover_image.url
                })
            cache.set(cache_key, json.dumps(search_results, indent=4), settings.CACHE_DEFAULT_TIMEOUT)
        return HttpResponse(Data(True, "Berhasil GET films from {}".format("Cache" if use_cached else "DB"), search_results).get_json())
    elif request.method == "POST":
        verify_user = AUTH.verify_admin(request)
        if verify_user[0]:
            genres = list(dict.fromkeys(request.POST.getlist('genre')))
            form_data = {
                "title": request.POST['title'],
                "description": request.POST['description'],
                "director": request.POST['director'],
                "release_year": int(request.POST['release_year']),
                "genre": genres,
                "price": int(request.POST['price']),
                "duration": int(request.POST['duration'])
            }
            post_request = request.POST.dict()
            post_request["genre"] = json.dumps(genres)
            updated_post_request = QueryDict('', mutable=True)
            updated_post_request.update(post_request)
            form = CreateFilm(updated_post_request, request.FILES)
            if form.is_valid():
                form.save()
                film_data = Film.objects.latest("created_at")
                form_data["id"] = str(film_data.id)
                form_data["video_url"] = film_data.video.url
                form_data["cover_image_url"] = film_data.cover_image.url
                form_data["created_at"] = film_data.created_at.isoformat()[:23]+"Z"
                form_data["updated_at"] = film_data.updated_at.isoformat()[:23]+"Z"
                cache.delete("films")
                cache.delete("main_video_data")
                cache.set("films:{}".format(form_data["id"]), json.dumps(form_data, indent=4), settings.CACHE_DEFAULT_TIMEOUT)
                for i in cache._cache.get_client().keys(":*:search_films:*"):
                    search_term = i.decode().split(":search_films:")[1]
                    if is_substr(form_data["title"], search_term) or is_substr(form_data["director"], search_term):
                        cache.delete("search_films:{}".format(search_term))
                return HttpResponse(Data(True, "Berhasil POST films", form_data).get_json())
            else:
                return ErrorPages.Error400("Gagal POST films", data=json.loads(form.errors.as_json()))
        else:
            return ErrorPages.Error401()
    else:
        return ErrorPages.Error405()

@csrf_exempt
def films_id(request, film_id):
    if request.method in ("GET", "PUT", "DELETE"):
        verify_user = AUTH.verify_bought_or_admin(request, str(film_id))
        if verify_user[0]:
            cache_key = "films:{}".format(str(film_id))
            cached_data = cache.get(cache_key)
            if request.method == "GET" and cached_data and cached_data != "":
                return HttpResponse(Data(True, "Berhasil GET films ID from Cache", json.loads(cached_data)).get_json())
            else:
                query = Film.objects.filter(id=film_id)
                if  len(query) == 0:
                    return ErrorPages.Error400("Gagal {} film".format(request.method))
                else:
                    film_data = {
                        "id": str(query[0].id),
                        "title": query[0].title,
                        "description": query[0].description,
                        "director": query[0].director,
                        "release_year": query[0].release_year,
                        "genre": json.loads(query[0].genre),
                        "price": query[0].price,
                        "duration": query[0].duration,
                        "video_url": query[0].video.url,
                        "cover_image_url": query[0].cover_image.url,
                        "created_at": query[0].created_at.isoformat()[:23]+"Z",
                        "updated_at": query[0].updated_at.isoformat()[:23]+"Z"
                    }
                    if request.method == "GET":
                        cache.set(cache_key, json.dumps(film_data, indent=4), settings.CACHE_DEFAULT_TIMEOUT)
                        return HttpResponse(Data(True, "Berhasil GET films ID from DB", film_data).get_json())
                    elif request.method == "PUT" and verify_user[1]["is_admin"] == True:
                        request.method = "POST"
                        genres = list(dict.fromkeys(request.POST.getlist('genre')))
                        film_data = {
                            "id": str(query[0].id),
                            "title": request.POST["title"],
                            "description": request.POST["description"],
                            "director": request.POST["director"],
                            "release_year": request.POST["release_year"],
                            "genre": genres,
                            "price": request.POST["price"],
                            "duration": request.POST["duration"],
                            "video_url": query[0].video.url,
                            "cover_image_url": query[0].cover_image.url,
                            "created_at": query[0].created_at.isoformat()[:23]+"Z",
                            "updated_at": query[0].updated_at.isoformat()[:23]+"Z"
                        }
                        query[0].update(
                            request.POST["title"],
                            request.POST["description"],
                            request.POST["director"],
                            request.POST["release_year"],
                            json.dumps(genres),
                            request.POST["price"],
                            request.POST["duration"]
                        )
                        if request.FILES.get("video"):
                            query[0].update_video(request.FILES["video"])
                        if request.FILES.get("cover_image"):
                            query[0].update_cover_image(request.FILES["cover_image"])
                        updated_time = timezone.now()
                        query[0].updated_at = updated_time
                        query[0].save()
                        updated_data = Film.objects.get(id=film_id)
                        film_data["updated_at"] = updated_time.isoformat()[:23]+"Z"
                        film_data["video_url"] = updated_data.video.url
                        film_data["cover_image_url"] = updated_data.cover_image.url
                        cache.delete("films")
                        cache.set(cache_key, json.dumps(film_data, indent=4), settings.CACHE_DEFAULT_TIMEOUT)
                        for i in cache._cache.get_client().keys(":*:search_films:*"):
                            search_term = i.decode().split(":search_films:")[1]
                            if is_substr(film_data["title"], search_term) or is_substr(film_data["director"], search_term):
                                cache.delete("search_films:{}".format(search_term))
                        return HttpResponse(Data(True, "Berhasil PUT films ID", film_data).get_json())
                    elif request.method == "DELETE" and verify_user[1]["is_admin"] == True:
                        response = HttpResponse(Data(True, "Berhasil DELETE films ID", film_data).get_json())
                        query[0].delete()
                        cache.delete("films")
                        cache.delete(cache_key)
                        for i in cache._cache.get_client().keys(":*:search_films:*"):
                            search_term = i.decode().split(":search_films:")[1]
                            if is_substr(film_data["title"], search_term) or is_substr(film_data["director"], search_term):
                                cache.delete("search_films:{}".format(search_term))
                        return response
                    else:
                        return ErrorPages.Error405()
        else:
            return ErrorPages.Error401()
    else:
        return ErrorPages.Error405()

@csrf_exempt
def login(request):
    if request.method == "POST":
        request_body = json.loads(request.body)
        request_username = request_body.get("username")
        request_password = request_body.get("password")
        if request_username and request_username != "" and request_password and request_password != "":
            query_by_username = Profile.objects.filter(username=request_username)
            query_by_email = Profile.objects.filter(email=request_username)
            query = (query_by_username | query_by_email).distinct()
            if len(query) == 0:
                # username tidak ditemukan
                return ErrorPages.Error400("Gagal LOGIN{}".format(": username tidak ditemukan" if settings.DEBUG else ""))
            else:
                if check_password(request_password, query[0].password):
                    return HttpResponse(Data(True, "Berhasil LOGIN", {
                    "username": query[0].username,
                    "token": JWT.sign(query[0].username, query[0].is_staff)
                }).get_json())
                else:
                    # password salah
                    return ErrorPages.Error400("Gagal LOGIN{}".format(": password salah" if settings.DEBUG else ""))
        else:
            # request tidak valid
            return ErrorPages.Error400("Gagal LOGIN{}".format(": request tidak valid" if settings.DEBUG else ""))
    else:
        return ErrorPages.Error405()

@csrf_exempt
def self(request):
    if request.method == "GET":
        verify_user = AUTH.verify_admin(request)
        if verify_user[0]:
            return HttpResponse(Data(True, "Berhasil GET self", {
                "username": verify_user[1]["username"],
                "token": JWT.sign(verify_user[1]["username"], verify_user[1]["is_admin"])
            }).get_json())
        else:
            return ErrorPages.Error401()
    else:
        return ErrorPages.Error405()

@csrf_exempt
def users(request):
    if request.method == "GET":
        verify_user = AUTH.verify_admin(request)
        if verify_user[0] and verify_user[1]["is_admin"] == True:
            use_cached = False
            cached_data = ""
            cache_key = ""
            search_data = {}
            search_results = []
            if request.GET.get('q') and request.GET['q'] != "":
                cache_key = "search_users:{}".format(request.GET['q'])
                cached_data = cache.get(cache_key)
                if cached_data and cached_data != "":
                    use_cached = True
                else:
                    search_data = Profile.objects.filter(is_staff=False).filter(is_active=True).filter(username__icontains = request.GET['q'])
            else:
                cache_key = "users"
                cached_data = cache.get(cache_key)
                if cached_data and cached_data != "":
                    use_cached = True
                else:
                    search_data = Profile.objects.filter(is_staff=False).filter(is_active=True)
            if use_cached:
                search_results = json.loads(cached_data)
            else:
                for i in search_data:
                    search_results.append({
                        "id": str(i.id),
                        "email": i.email,
                        "username": i.username,
                        "balance": i.balance
                    })
                cache.set(cache_key, json.dumps(search_results, indent=4), settings.CACHE_DEFAULT_TIMEOUT)
            return HttpResponse(Data(True, "Berhasil GET users from {}".format("Cache" if use_cached else "DB"), search_results).get_json())
        else:
            return ErrorPages.Error401()
    else:
        return ErrorPages.Error405()

@csrf_exempt
def users_id(request, user_id):
    if request.method in ("GET", "DELETE"):
        verify_user = AUTH.verify_admin(request)
        if verify_user[0] and verify_user[1]["is_admin"] == True:
            cache_key = "users:{}".format(user_id)
            cached_data = cache.get(cache_key)
            if request.method == "GET" and cached_data and cached_data != "":
                return HttpResponse(Data(True, "Berhasil GET users from Cache", json.loads(cached_data)).get_json())
            else:
                query = Profile.objects.filter(id=user_id)
                if  len(query) == 0:
                    return ErrorPages.Error400("Gagal {} user".format(request.method))
                else:
                    user_data = {
                        "id": str(query[0].id),
                        "username": query[0].username,
                        "email": query[0].email,
                        "balance": query[0].balance,
                    }
                    if request.method == "GET":
                        cache.set(cache_key, json.dumps(user_data, indent=4), settings.CACHE_DEFAULT_TIMEOUT)
                        return HttpResponse(Data(True, "Berhasil GET users ID from DB", user_data).get_json())
                    elif request.method == "DELETE":
                        response = HttpResponse(Data(True, "Berhasil DELETE users ID", user_data).get_json())
                        query[0].delete()
                        cache.delete("users")
                        cache.delete(cache_key)
                        for i in cache._cache.get_client().keys(":*:search_users:*"):
                            search_term = i.decode().split(":search_users:")[1]
                            if is_substr(user_data["username"], search_term):
                                cache.delete("search_users:{}".format(search_term))
                        return response
                    else:
                        return ErrorPages.Error405()
        else:
            return ErrorPages.Error401()
    else:
        return ErrorPages.Error405()

@csrf_exempt
def users_id_balance(request, user_id):
    if request.method == "POST":
        verify_user = AUTH.verify_admin(request)
        if verify_user[0] and verify_user[1]["is_admin"] == True:
            cache_key = "users:{}".format(user_id)
            query = Profile.objects.filter(id=user_id)
            if  len(query) == 0:
                return ErrorPages.Error400("Gagal POST users balance")
            else:
                final_balance = query[0].balance + json.loads(request.body)["increment"]
                updated_balance = final_balance if final_balance > 0 else 0
                query[0].balance = updated_balance
                query[0].save()
                user_data = {
                    "id": str(query[0].id),
                    "username": query[0].username,
                    "email": query[0].email,
                    "balance": updated_balance,
                }
                cache.delete("users")
                cache.set(cache_key, json.dumps(user_data, indent=4), settings.CACHE_DEFAULT_TIMEOUT)
                return HttpResponse(Data(True, "Berhasil POST users balance", user_data).get_json())
        else:
            return ErrorPages.Error401()
    else:
        return ErrorPages.Error405()

@csrf_exempt
def buy(request, film_id):
    if request.method == "POST":
        verify_user = AUTH.verify_admin(request)
        if verify_user[0]:
            users_id = verify_user[1]["id"]
            cache_key = ["users", "users-bought:{}".format(users_id), "users:{}".format(users_id)]
            user_data = Profile.objects.filter(id=users_id)
            if  len(user_data) == 0:
                return ErrorPages.Error400("Gagal POST buy{}".format(": user not found" if settings.DEBUG else ""))
            else:
                if str(film_id) in json.loads(user_data[0].bought_movies):
                    return ErrorPages.Error400("Film telah dibeli")
                else:
                    film_data = Film.objects.filter(id=film_id)
                    if  len(film_data) == 0:
                        return ErrorPages.Error400("Gagal POST buy{}".format(": film not found" if settings.DEBUG else ""))
                    else:
                        if user_data[0].balance >= film_data[0].price:
                            user_data[0].balance = user_data[0].balance - film_data[0].price
                            bought_data = json.loads(user_data[0].bought_movies)
                            bought_data.append(str(film_id))
                            user_data[0].bought_movies = json.dumps(bought_data)
                            updated_balance = user_data[0].balance
                            user_data[0].save()
                            for i in cache_key:
                                cache.delete(i)
                            for i in cache._cache.get_client().keys(":*:search_users:*"):
                                search_term = i.decode().split(":search_users:")[1]
                                if is_substr(user_data[0].username, search_term):
                                    cache.delete("search_users:{}".format(search_term))
                            user_data = {
                                "id": str(user_data[0].id),
                                "username": user_data[0].username,
                                "email": user_data[0].email,
                                "balance": updated_balance,
                            }
                            cache.set("users:{}".format(user_data["id"]), json.dumps(user_data))
                            return HttpResponse(Data(True, "Berhasil POST buy", json.dumps(user_data)).get_json())
                        else:
                            return ErrorPages.Error400("Gagal POST buy{}".format(": insufficient balance" if settings.DEBUG else ""))
                    
        else:
            return ErrorPages.Error401()
    else:
        return ErrorPages.Error405()

@csrf_exempt
def bought(request):
    if request.method == "GET":
        verify_user = AUTH.verify_admin(request)
        if verify_user[0]:
            users_id = verify_user[1]["id"]
            cache_key = "users-bought:{}".format(users_id)
            users_bought_cache = cache.get(cache_key)
            if users_bought_cache and users_bought_cache != "":
                return HttpResponse(Data(True, "Berhasil GET users bought from DB", json.loads(users_bought_cache)).get_json())
            else:
                query = Profile.objects.filter(id=users_id)
                if  len(query) == 0:
                    return ErrorPages.Error400("Gagal GET users bought")
                else:
                    bought_data = json.loads(query[0].bought_movies)
                    cache.set(cache_key, json.dumps(bought_data, indent=4), settings.CACHE_DEFAULT_TIMEOUT)
                    return HttpResponse(Data(True, "Berhasil GET users bought from DB", bought_data).get_json())
        else:
            return ErrorPages.Error401()
    else:
        return ErrorPages.Error405()