from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import os
import pytz
import uuid

class Profile(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=256, unique=True)
    balance = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    bought_movies = models.TextField(default="[]")

    REQUIRED_FIELDS = ['email', 'first_name']

class Film(models.Model):
    def video_filename_renamer(instance, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (instance.id, ext)
        return os.path.join('videos', filename)

    def cover_image_filename_renamer(instance, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (instance.id, ext)
        return os.path.join('cover_images', filename)
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=256, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    director = models.CharField(max_length=256, null=False, blank=False)
    release_year = models.IntegerField(null=False, blank=False)
    genre = models.TextField(default="[]", null=False, blank=False)
    price = models.IntegerField(null=False, blank=False)
    duration = models.IntegerField(null=False, blank=False)
    video = models.FileField(upload_to=video_filename_renamer, null=False, blank=False)   
    cover_image = models.ImageField(upload_to=cover_image_filename_renamer, null=True, blank=True)
    creation_time = timezone.now
    created_at = models.DateTimeField(default=creation_time, editable=False, null=False, blank=False)
    updated_at = models.DateTimeField(default=creation_time, editable=False, null=False, blank=False)

    REQUIRED_FIELDS = ['title', 'description', 'director', 'release_year', 'genre', 'price', 'duration', 'video']

    def update(self, new_title, new_description, new_director, new_release_year, new_genre, new_price, new_duration):
        self.title = new_title
        self.description = new_description
        self.director = new_director
        self.release_year = new_release_year
        self.genre = new_genre
        self.price = new_price
        self.duration = new_duration

    def update_video(self, new_video):
        self.video.delete()
        self.video = new_video

    def update_cover_image(self, new_cover_image):
        self.cover_image.delete()
        self.cover_image = new_cover_image

    def delete(self):
        self.video.delete()
        self.cover_image.delete()
        super().delete()