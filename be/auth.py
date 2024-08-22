from be.models import Profile
from django.conf import settings

import datetime
import json
import jwt
import pytz

class JWT:
    def sign(username: str, is_admin: bool):
        return jwt.encode(
            {
                "user": username,
                "is_admin": is_admin,
                "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1)
            },
            settings.ACCESS_TOKEN_SECRET, 
            algorithm=settings.JWT_ALGORITHM
        )

    def verify(token: str):
        try:
            verify_token = jwt.decode(
                    token,
                    settings.ACCESS_TOKEN_SECRET,
                    algorithms=settings.JWT_ALGORITHM
            )
        except:
            return (False, {})
        return (True, {
            "username": verify_token["user"],
            "is_admin": verify_token["is_admin"]
        })

    def sign_audience(id: str):
        return jwt.encode(
            {
                "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1),
                "aud": id
            },
            settings.ACCESS_TOKEN_SECRET, 
            algorithm=settings.JWT_ALGORITHM
        )

    def verify_audience(id: str, token: str):
        try:
            verify_token = jwt.decode(
                    token,
                    settings.ACCESS_TOKEN_SECRET,
                    audience=id,
                    algorithms=settings.JWT_ALGORITHM
            )
        except:
            return False
        return True

class AUTH:
    def verify_admin(request):
        if request.META.get('HTTP_AUTHORIZATION'):
            bearer_token = request.META['HTTP_AUTHORIZATION'].split()[1]
            jwt_auth = JWT.verify(bearer_token)
            if jwt_auth[0]:
                user_data = Profile.objects.filter(username=jwt_auth[1]["username"])
                if len(user_data) > 0 and user_data[0].is_staff == jwt_auth[1]["is_admin"]:
                    return (True, {
                        "id": str(user_data[0].id),
                        "username": jwt_auth[1]["username"],
                        "is_admin": jwt_auth[1]["is_admin"],
                        "token": bearer_token
                    })
                else:
                    return (False, {})
            else:
                return (False, {})
        else:
            return (False, {})

    def verify_bought_or_admin(request, film_id):
        if request.META.get('HTTP_AUTHORIZATION'):
            bearer_token = request.META['HTTP_AUTHORIZATION'].split()[1]
            jwt_auth = JWT.verify(bearer_token)
            if jwt_auth[0]:
                user_data = Profile.objects.filter(username=jwt_auth[1]["username"])
                if len(user_data) > 0 and (
                    user_data[0].is_staff == True
                    or
                    film_id in json.loads(user_data[0].bought_movies)
                ):
                    return (True, {
                        "id": str(user_data[0].id),
                        "username": jwt_auth[1]["username"],
                        "is_admin": jwt_auth[1]["is_admin"],
                        "token": bearer_token
                    })
                else:
                    return (False, {})
            else:
                return (False, {})
        else:
            return (False, {})