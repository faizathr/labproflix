
# Labproflix

## Installation
- git clone https://github.com/faizathr/labproflix.git
- cd labproflix
- Fill .env Environment Variables
- python -m venv venv
- source venv/bin/activate or venv/Scripts/activate.bat
- pip install -r requirements.txt
- Point labpro.local to 127.0.0.1 (localhost) and makesure it's wildcard (*.labpro.local)
    - /etc/hosts
        ```
        127.0.0.1 labpro.local
        127.0.0.1 api.labpro.local
        ```
- Configure domain in labpro/hosts.py if neccessary
- docker compose up -d 
    (make sure postgresql and redis-server is up)
-  psql -h localhost -p 5432 -U admin labpro < top_10_movies.sql
    - Django Admin Credentials
        - username: admin
        - password: yvd5CC@y^lQ6!iIdV%!2W^ZnpRXhD5L&
- python manage.py runserver

## Design Pattern
- Facade
    - Login: Receive credential, verify, create token, checking permissions and so on, is a complex procedure, by using AUTH class in labpro/auth.py, login procedure is simplified
- Iterator
    - Search query is cached using Redis to improve performance. To delete outdated cache, we have to iterate through each cached search query if the cached search query is a substring of a column of the new updated row of data 
- Adapter
    - data attribute of Data Class (Class to construct REST API output) is constructed with json. To make HttpResponse can output the Data.data, it has to be converted to string first by .get_json() method 

## Tech Stacks
- Framework: 
    - Backend: Django
    - Frontend: Vanilla html and js with django template engine and CSS generated from Tailwind CSS
- Database: PostgreSQL
- Cache: Redis
- S3 Bucket: Cloudflare R2
- Static File: Whitenoise
- Deployment:
    - OS: Linux VPS
    - Containerization: Docker
    - Reverse Proxy: Gunicorn & Nginx

## Endpoints
- Backend
    - /
    - /admin/
    - /browse,
    - /accounts/
    - /accounts/signup/
    - /accounts/signup/activation-sent
    - /activate/:uuid/:token/
- API
    - /
    - /films
    - /films/:film_id
    - /login
    - /self
    - /users
    - /bought
    - /buy/:film_id
    - /users/:user_id
    - /users/:user_id/balance

## Bonus

### B02 - Deployment
- Backend: https://labproflix.faizath.com
- API: https://api.labproflix.faizath.com

### B03 - Polling
Menggunakan short polling tiap 1 menit pada fe/ browse.html
```javascript
movieListPoll = setInterval(listMovie, 1 * 60 * 1000);
```

### B04 - Caching
Menggunakan caching server Redis

### B10 - Fitur Tambahan
- Email confirmation pada saat registration
- Change password
- Forgot password menggunakan email

### B11 - Ember
Menggunakan Cloudflare R2

## Author
- Muhammad Faiz Atharrahman
- 18222063