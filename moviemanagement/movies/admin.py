from django.contrib import admin # type: ignore

from .models import Genre, Person, Movie, MovieCast, Language, MovieLanguage, Review, Users

admin.site.register(Genre)
admin.site.register(Person)
admin.site.register(Movie)
admin.site.register(MovieCast)
admin.site.register(Language)
admin.site.register(MovieLanguage)
admin.site.register(Review)
admin.site.register(Users)