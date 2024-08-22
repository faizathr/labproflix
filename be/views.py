from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from .forms import RegisterForm
from .auth import JWT
from .models import Profile, Film

import datetime
import json
import requests

def activate(request, uuid, token):
    if JWT.verify_audience(str(uuid), token):
        user = Profile.objects.get(id=str(uuid))
        if user.is_active:
            return render(request, 'prompt.html', {
                "title": "Already Verified",
                "text1": "Already Verified",
                "text2": "Login to your account",
                "button": "Login",
                "button_url": reverse("login")
            })
        else:
            cache.delete("users")
            for i in cache._cache.get_client().keys(":*:search_users:*"):
                search_term = i.decode().split(":search_users:")[1]
                if is_substr(user.username, search_term):
                    cache.delete("search_users:{}".format(search_term))
            user.is_active = True
            user.save()
            login(request, user)
            return render(request, 'prompt.html', {
                "title": "Email Verified",
                "text1": "Email Verified",
                "text2": "Your account is successfully activated",
                "button": "Browse",
                "button_url": reverse("browse")
            })
    else:
        return render(request, 'prompt.html', {
            "title": "Activation Invalid",
            "text1": "Activation Invalid",
            "text2": "Please re register your account",
            "button": "Register",
            "button_url": reverse("signup")
        })

def signup(request):
    if request.method  == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user_data = Profile.objects.latest("date_joined")
            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            message = render_to_string('registration/activation_request.html', {
                'user': user_data.username,
                'domain': current_site.domain,
                'protocol': 'http://',
                'uuid': str(user_data.id),
                'token': JWT.sign_audience(str(user_data.id)),
            })
            user_data.email_user(subject, message)
            return redirect('activation_sent')
        else:
            form = RegisterForm()
    else:
        form = RegisterForm()
    return render(request, 'registration/signup.html', {'form': form})

def activation_sent(request):
    return render(request, 'prompt.html', {
        "title": "Activation Sent",
        "text1": "Activation Sent",
        "text2": "Check your email inbox (or your spam) to activate your account",
        "button": "Login",
        "button_url": reverse("login")
    })

def browse(request):
    main_video_data_cache = cache.get("main_video_data")
    if main_video_data_cache and main_video_data_cache != "":
        main_video_data = json.loads(main_video_data_cache)
    else:
        main_video = Film.objects.all().order_by('-created_at')
        if len(main_video) > 0:
            main_video_title = main_video[0].title
            main_video_id = str(main_video[0].id)
            main_video_description = main_video[0].description
            main_video_release_year = str(main_video[0].release_year)
            main_video_genres = ", ".join(json.loads(main_video[0].genre))
            main_video_duration = str(datetime.timedelta(seconds=main_video[0].duration))
            main_video_director = main_video[0].director
            main_video_price = str(main_video[0].price)
            main_video_cover_image_url = main_video[0].cover_image.url

            main_video_yt_id_cache = cache.get("yt-id:{}".format(main_video_id))
            if main_video_yt_id_cache and main_video_yt_id_cache != "":
                main_video_yt_id = main_video_yt_id_cache
            else:
                main_video_yt_id = json.loads(requests.get("https://inv.altsite.org/api/v1/search?q={}+({})+trailer".format(
                    main_video_title,
                    main_video_release_year
                )).text)[0]["videoId"]
                cache.set("yt-id:{}".format(main_video_id), main_video_yt_id, 24 * 3600)

            main_video_youtube_url_cache = cache.get("yt-url:{}".format(main_video_id))
            if main_video_youtube_url_cache and main_video_youtube_url_cache != "":
                main_video_youtube_url = main_video_youtube_url_cache
            else:
                main_video_youtube_url = json.loads(requests.get("https://inv.altsite.org/api/v1/videos/" + main_video_yt_id).text)["formatStreams"][0]["url"]
                cache.set("yt-url:{}".format(main_video_id), main_video_youtube_url, 4 * 3600)
            
            main_video_data = {
                "id": main_video_id,
                "title": main_video_title,
                "director": main_video_director,
                "price": main_video_price,
                "description": main_video_description,
                "release_year": main_video_release_year,
                "genres": main_video_genres,
                "duration": main_video_duration,
                "cover_image_url": main_video_cover_image_url,
                "yt_id": main_video_yt_id,
                "youtube_url": main_video_youtube_url
            }

            cache.set("main_video_data", json.dumps(main_video_data), 1 * 3600)
        

    if request.user.is_authenticated:
        signin_account_button = '''
        <button form="changepassword" type="submit" class=" h-8 lg:h-10 text-white px-4 bg-[rgb(229,9,20)] rounded-md hover:bg-red-700 font-bold hover:duration-500">Change Password</button>
        <button form="logout" type="submit" class=" h-8 lg:h-10 text-white px-4 bg-[rgb(229,9,20)] rounded-md hover:bg-red-700 font-bold hover:duration-500">Log out</button>
        '''
        if main_video_data["id"] in json.loads(request.user.bought_movies):
            popup_video_button = '''<button id='popup-video-play-button' class="bg-white rounded-md py-1 px-2 md:py-2 md:px-4 w-auto text-xs lg:text-lg font-semibold flex flex-row items-center hover:bg-neutral-300 transition">
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16" height="24" width="24" xmlns="http://www.w3.org/2000/svg">
                    <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>
                </svg>
                Play
            </button>

            <button id='popup-video-buy-button' class="hidden bg-white rounded-md py-1 px-2 md:py-2 md:px-4 w-auto text-xs lg:text-lg font-semibold flex flex-row items-center hover:bg-neutral-300 transition">
                <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="1 -5 30 30">
                    <path fill="currentColor" d="M0 1h4.764l.545 2h18.078l-3.666 11H7.78l-.5 2H22v2H4.72l1.246-4.989L3.236 3H0V1Zm7.764 11h10.515l2.334-7H5.855l1.909 7ZM4 21a2 2 0 1 1 4 0a2 2 0 0 1-4 0Zm14 0a2 2 0 1 1 4 0a2 2 0 0 1-4 0Z"/>
                </svg>
                Buy
            </button>
            '''
        else:
            popup_video_button = '''
            <button id='popup-video-buy-button' class="bg-white rounded-md py-1 px-2 md:py-2 md:px-4 w-auto text-xs lg:text-lg font-semibold flex flex-row items-center hover:bg-neutral-300 transition">
                <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="1 -5 30 30">
                    <path fill="currentColor" d="M0 1h4.764l.545 2h18.078l-3.666 11H7.78l-.5 2H22v2H4.72l1.246-4.989L3.236 3H0V1Zm7.764 11h10.515l2.334-7H5.855l1.909 7ZM4 21a2 2 0 1 1 4 0a2 2 0 0 1-4 0Zm14 0a2 2 0 1 1 4 0a2 2 0 0 1-4 0Z"/>
                </svg>
                Buy
            </button>

            <button id='popup-video-play-button' class="hidden bg-white rounded-md py-1 px-2 md:py-2 md:px-4 w-auto text-xs lg:text-lg font-semibold flex flex-row items-center hover:bg-neutral-300 transition">
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16" height="24" width="24" xmlns="http://www.w3.org/2000/svg">
                    <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>
                </svg>
                Play
            </button>
            '''
    else:
        signin_account_button = '''<button form="login" type="submit" class=" h-8 lg:h-10 text-white px-4 bg-[rgb(229,9,20)] rounded-md hover:bg-red-700 font-bold hover:duration-500">
            Sign In
          </button>'''
        popup_video_button = '''
          <button form="login" type="submit" class="bg-white rounded-md py-1 px-2 md:py-2 md:px-4 w-auto text-xs lg:text-lg font-semibold flex flex-row items-center hover:bg-neutral-300 transition">
              <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="1 -5 30 30">
                  <path fill="currentColor" d="M0 1h4.764l.545 2h18.078l-3.666 11H7.78l-.5 2H22v2H4.72l1.246-4.989L3.236 3H0V1Zm7.764 11h10.515l2.334-7H5.855l1.909 7ZM4 21a2 2 0 1 1 4 0a2 2 0 0 1-4 0Zm14 0a2 2 0 1 1 4 0a2 2 0 0 1-4 0Z"/>
              </svg>
              Buy
          </button>

            <button id='popup-video-play-button' class="hidden bg-white rounded-md py-1 px-2 md:py-2 md:px-4 w-auto text-xs lg:text-lg font-semibold flex flex-row items-center hover:bg-neutral-300 transition">
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16" height="24" width="24" xmlns="http://www.w3.org/2000/svg">
                    <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z"></path>
                </svg>
                Play
            </button>
        '''
    return render(request,("browse.html"), {
        "popup_video_button": popup_video_button,
        "signin_account_button": signin_account_button,
        "main_video_data": main_video_data
    })