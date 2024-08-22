"""
URL configuration for labpro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path('', views.index, name='index'),
    path('films', views.films, name='films'),
    path('films/<uuid:film_id>', views.films_id, name='films_id'),
    path('login', views.login, name='login'),
    path('self', views.self, name='self'),
    path('users', views.users, name='users'),
    path('bought', views.bought, name='bought'),
    path('buy/<uuid:film_id>', views.buy, name='buy'),
    path('users/<uuid:user_id>', views.users_id, name='users_id'),
    path('users/<uuid:user_id>/balance', views.users_id_balance, name='users_id_balance'),
]