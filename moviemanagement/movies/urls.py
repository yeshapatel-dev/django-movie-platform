from django.urls import path # type: ignore
from . import views

app_name = "movies"

urlpatterns = [
    path('registration/', views.RegistrationView.as_view(), name='registration'),
    path('signin/', views.SigninView.as_view(), name='signin'),
    path('signout/', views.SignoutView.as_view(), name='signout'),

    path('homepage/', views.HomePageView.as_view(), name='home'),

    path('moviepage/', views.MoviePageView.as_view(), name='movie'),
    path('addmoviepage/', views.AddEditMovieView.as_view(), name='addmovie'),
    path('editmoviepage/<int:movie_id>/', views.AddEditMovieView.as_view(), name='editmovie'), ##
    path('deletemovie/<int:pk>/', views.DeleteMovie.as_view(), name='deletemovie'),
    path('movieDetailpage/<int:movie_id>/', views.MovieDetailView.as_view(), name='movieDetail'),

    path('movie/manage_cast_language/<int:movie_id>/', views.ManageCastLanguagesView.as_view(), name='manage_cast_language'),
    path('removecast/<int:pk>/', views.RemoveCast.as_view(), name='removeCast'),
    path('removelanguage/<int:pk>/', views.RemoveLanguage.as_view(), name='removeLanguage'),
    
    path('genrepage/', views.GenrePageView.as_view(), name='genre'),
    path('addgenrepage/', views.AddEditGenreView.as_view(), name='addgenre'),
    path('editgenre/<int:genre_id>/', views.AddEditGenreView.as_view(), name='editgenre'),
    path('deletegenre/<int:pk>/', views.DeleteGenre.as_view(), name='deletegenre'),

    
    path('peoplepage/', views.PersonListView.as_view(), name='people'),
    path('addpeoplepage/', views.AddEditPeopleView.as_view(), name='addpeople'),
    path('editpeoplepage/<int:person_id>/', views.AddEditPeopleView.as_view(), name='editpeople'), ##
    path('deletepeople/<int:pk>/', views.DeletePeople.as_view(), name='deletepeople'),
    path('personDetailpage/<int:person_id>/', views.PersonDetailView.as_view(), name='personDetail'),

    path('addreviewpage/<int:movie_id>/', views.AddEditReview.as_view(), name='addreview'),
    path('editreviewpage/<int:movie_id>/<int:review_id>/', views.AddEditReview.as_view(), name='editreview'),
    path('deletereview/<int:pk>/', views.DeleteReview.as_view(), name='deletereview'),
]