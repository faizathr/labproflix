from django import forms
from be.models import Film

class CreateFilm(forms.ModelForm):
    class Meta:
        model = Film
        fields = ('title', 'description', 'director', 'release_year', 'genre', 'price', 'duration', 'video', 'cover_image')