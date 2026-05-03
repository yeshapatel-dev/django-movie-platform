from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.views import View # type: ignore
from django.views.generic import TemplateView, ListView, DeleteView, FormView, View # type: ignore
from django.views.decorators.csrf import csrf_protect # type: ignore
from django.utils.decorators import method_decorator # type: ignore
from django.views.decorators.cache import never_cache # type: ignore
from movies.models import Genre, Person, Movie, MovieCast, Language, MovieLanguage, Review
from datetime import date
from django.urls import reverse_lazy, reverse, resolve # type: ignore
from django.contrib import messages # type: ignore
from django.db.models import Avg # type: ignore 
from django.contrib.auth.views import LoginView, LogoutView # type: ignore
from django.views.generic.edit import FormView # type: ignore
from django.contrib.auth import login, logout, authenticate # type: ignore
from .form import RegistrationForm, SigninForm # type: ignore
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # type: ignore
from .mixins import AdminRequiredMixin, UserAccessMixin, ReviewAuthorMixin
from .models import Users

# Home
class HomePageView(TemplateView):
    model = Movie
    template_name = 'movies/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        # filter on genre
        # context['movies'] = Movie.objects.all()
        selected_genre = self.request.GET.get('genres')
        if selected_genre:
            context['movies'] = Movie.objects.filter(genre__name=selected_genre)
        else:
            context['movies'] = Movie.objects.all()
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search_query')
        genres_list = self.request.GET.getlist('genres')
        if search_query :
            queryset = queryset.filter(title_icontains=search_query)
        # if search_query:
        #     queryset = queryset.filter(person_name__icontains=search_query)
        if genres_list :
            queryset = queryset.filter(genre__in=genres_list)
        return queryset

# Movie
# class MoviePageView(LoginRequiredMixin, AdminRequiredMixin, ListView):
class MoviePageView(UserAccessMixin, ListView):
    model = Movie
    template_name = 'movies/movie.html'
    context_object_name = 'movies'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        context['years'] = Movie.objects.values_list('release_year', flat=True).distinct().order_by('-release_year')

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        print("movie list printing..")

        genres_list = self.request.GET.getlist('genres')
        print(f"genre: {genres_list}") ## 
        selected_year = self.request.GET.get('year')
        print(f"selected_year: {selected_year}") ##
        search_query = self.request.GET.get('search_movie')
        print(f"search_query: {search_query}") ## 

        if genres_list and 'all' not in [g.lower() for g in genres_list]:
            print("filter with genre block..")
            queryset = queryset.filter(genre__genre_name__in=genres_list)
        if selected_year and selected_year != "all":
            print("filter with year block..")
            queryset = queryset.filter(release_year=selected_year)
        if search_query:
            print("filter with search-query block..")
            queryset = queryset.filter(title__icontains=search_query)
        
        return queryset
        

@method_decorator(csrf_protect, name='dispatch')
class AddEditMovieView(View):
    template_name = 'movies/addmovie.html'

    def get(self, request, movie_id=None, *args, **kwargs):
        movie = None
        if movie_id:
            movie = get_object_or_404(Movie, id=movie_id)

        genres = Genre.objects.all()
        directors = Person.objects.filter(role_type=Person.Role.DIRECTOR)

        context = {
            'movie': movie,
            'genres': genres, 
            'directors': directors
        }
        return render(request, self.template_name, context)

    def post(self, request, movie_id=None, *args, **kwargs):
        print("Entering AddMovieView POST block")

        title = request.POST.get('title')
        description = request.POST.get('description')
        release_year = request.POST.get('release_year')
        duration = request.POST.get('duration')
        genre_name = request.POST.get('genre') or request.POST.get('genre_name')
        director_id = request.POST.get('director')
        uploaded_poster = request.FILES.get('poster') 

        print("FILES:", request.FILES)
        print("uploaded_poster:", uploaded_poster)
        
        if title:
            genre_obj = None
            if genre_name:
                # try:
                    if genre_name.isdigit():
                        genre_obj = Genre.objects.filter(id=int(genre_name)).first()
                    else:
                        genre_obj = Genre.objects.filter(genre_name__iexact=genre_name).first()
                # except Exception as e:
                #     print("Genre lookup error:", e)

            director_obj = None
            if director_id:
                # try:
                    if director_id.isdigit():
                        director_obj = Person.objects.filter(
                            id=int(director_id),
                            role_type=Person.Role.DIRECTOR
                        ).first()
                # except Exception as e:
                #     print("Director lookup error:", e)

            try:
                if movie_id:
                    movie = get_object_or_404(Movie, id=movie_id)
                    movie.title = title
                    movie.description = description or None
                    movie.release_year = int(release_year) if release_year and release_year.isdigit() else None
                    movie.duration = int(duration) if duration and duration.isdigit() else None
                    movie.genre = genre_obj
                    movie.director = director_obj

                    if uploaded_poster:
                        movie.poster = uploaded_poster

                    movie.save()
                    print(f"Updated movie: {movie}")

                else:
                    movie = Movie.objects.create(
                    title=title,
                    description=description or None,
                    release_year=int(release_year) if release_year and release_year.isdigit() else None,
                    duration=int(duration) if duration and duration.isdigit() else None,
                    genre=genre_obj,
                    director=director_obj,
                    poster=uploaded_poster
                )
                print(f"Created movie: {movie}")
                # redirect to manage cast/language after adding
                return redirect('movies:manage_cast_language', movie_id=movie.id)
            except Exception as e:
                print("Error creating movie:", e)

        genres = Genre.objects.all()
        directors = Person.objects.filter(role_type=Person.Role.DIRECTOR)
        context = {
            'movies': get_object_or_404(Movie, id=movie_id) if movie_id else None,
            'genres': genres, 
            'directors': directors
        }
        return render(request, self.template_name, context)

class DeleteMovie(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Movie
    success_url = reverse_lazy("movies:movie")
    template_name = 'movies/confirmation.html'
    # queryset = Movie.objects.all()

class MovieDetailView(TemplateView):
    template_name = 'movies/movieDetail.html'

    def get(self, request, movie_id, *args, **kwargs):
        movie = get_object_or_404(Movie, id=movie_id)
        cast = MovieCast.objects.filter(movie_name=movie)
        languages = MovieLanguage.objects.filter(movie_name=movie)
        # reviews = movie.reviews.all()  # uses related_name in Review model
        context = {
            'movie': movie,
            'cast': cast,
            'languages': languages,
            # 'reviews': reviews,
        }
        return render(request, self.template_name, context)

#People #peoplepageview
# class PersonListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
class PersonListView(UserAccessMixin, ListView):
    model = Person
    template_name = 'movies/people.html'
    context_object_name = 'people'

    def get_queryset(self):
        queryset = super().get_queryset()
        print(f"Initial queryset count: {queryset.count()}") ##

        role_type = self.request.GET.get('role_type')
        search_query = self.request.GET.get('search_person')

        print(f"role_type: {role_type}") ## 
        print(f"search_query: {search_query}") ##

        if role_type and role_type != "all":
            queryset = queryset.filter(role_type=role_type)
            print(f"Filtered by role_type. New count: {queryset.count()}") ##
        # else:
        #     queryset = Person.objects.all()
        #     print(f"Display all role type. count: {queryset.count()}") #3

        if search_query:
            queryset = queryset.filter(person_name__icontains=search_query)
            print(f"Filtered by search_query. New count: {queryset.count()}") ##

        print(f"Final queryset count: {queryset.count()}") ##

        return queryset#.order_by('person_name')
    
class DeletePeople(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Person
    success_url = reverse_lazy("movies:people")
    template_name = 'movies/confirmation.html'

class PersonDetailView(TemplateView):
    template_name = 'movies/personDetail.html'
    
    def get(self, request, person_id, *args, **kwargs):
        person = get_object_or_404(Person, id=person_id)
        directed_movies = person.directed_movies.all()
        acted_movie_casts = MovieCast.objects.filter(person=person).select_related('movie_name')

        context = {
            'person': person,
            'directed_movies': directed_movies,
            'acted_movie_casts': acted_movie_casts,
        }
        return render(request, self.template_name, context)

@method_decorator(csrf_protect, name='dispatch')
class AddEditPeopleView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = 'movies/addpeople.html'

    def get(self, request, person_id=None, *args, **kwargs):
        person = None
        if person_id:
            person = get_object_or_404(Person, id=person_id)

        context = {
            'person': person,
            'role_choices': Person.Role.choices
        }
        return render(request, self.template_name, context)

    def post(self, request, person_id=None, *args, **kwargs):
        print("Entering AddPeopleView POST block")

        person_name = request.POST.get('person_name')
        role_type = request.POST.get('role_type')
        birth_date_str = request.POST.get('birth_date')
        bio = request.POST.get('bio')
        profile_photo = request.FILES.get('profile_photo')

        print("FILES:", request.FILES)
        print("uploaded_poster:", profile_photo)

        if person_id:
            person = get_object_or_404(Person, id=person_id)
            
        else:
            person = Person()

        if birth_date_str:
            try:
                person.birth_date = date.fromisoformat(birth_date_str)
            except ValueError:
                person.birth_date = None
        else:
            person.birth_date = None

        person.person_name=person_name
        person.role_type=role_type
        person.bio=bio

        if profile_photo:
                person.profile_photo = profile_photo
        person.save()
        
        return redirect('movies:people')

# Genre
# class GenrePageView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
class GenrePageView(UserAccessMixin, TemplateView):
    template_name = 'movies/genre.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        return context

@method_decorator(csrf_protect, name='dispatch')
class AddEditGenreView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = 'movies/addgenre.html'

    def get(self, request, genre_id=None, *args, **kwargs):
        genre = None
        if genre_id:
            genre = get_object_or_404(Genre, id=genre_id)
        
        context = {
            'genre': genre
        }
        return render(request, self.template_name, context)

    def post(self, request, genre_id=None, *args, **kwargs):
        genre_name = request.POST.get('genre_name')
        
        if not genre_name:
            messages.error(request, "Genre name cannot be empty.")
            return redirect(self.request.path)

        try:
            if genre_id:
                genre = get_object_or_404(Genre, id=genre_id)
                genre.genre_name = genre_name
                genre.save()
                print(f"Updated genre: {genre}")
            else:
                genre = Genre.objects.create(genre_name=genre_name)
                print(f"Created genre: {genre}")
            
            # genre.genre_name = genre_name
            # genre.save()

            return redirect('movies:genre')
        
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect(self.request.path)


class DeleteGenre(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy("movies:genre")
    template_name = 'movies/confirmation.html'
    
# cast and lang
@method_decorator(csrf_protect, name='dispatch')
class ManageCastLanguagesView(LoginRequiredMixin, AdminRequiredMixin, View):
    template_name = 'movies/manage_cast_language.html'

    def get(self, request, movie_id, *args, **kwargs):
        movie = get_object_or_404(Movie, id=movie_id)
        actors = Person.objects.filter(role_type=Person.Role.ACTOR)
        languages =  Language.objects.all() # MovieLanguage.objects.all() {1:'English', 2:'Spanish', 3:'French', 4:'Filipino'}
        cast_list = MovieCast.objects.filter(movie_name=movie)
        movie_languages = MovieLanguage.objects.filter(movie_name=movie)

        context = {
            'movie': movie,
            'actors': actors,
            'languages': languages,
            'cast_list': cast_list,
            'movie_languages': movie_languages,
        }
        return render(request, self.template_name, context)

    def post(self, request, movie_id, *args, **kwargs):
        movie = get_object_or_404(Movie, id=movie_id)

        if 'add_cast' in request.POST:
            actor_id = request.POST.get('actor')
            character_name = request.POST.get('character_name')

            if not actor_id or not character_name:
                messages.error(request, "Please select an actor and enter a character name.", extra_tags="cast")
                return redirect(request.path)

            actor = Person.objects.filter(id=actor_id, role_type=Person.Role.ACTOR).first()
            if not actor:
                messages.error(request, "Invalid actor selection.", extra_tags="cast")
                return redirect(request.path)

            if MovieCast.objects.filter(movie_name=movie, person=actor).exists():
                messages.error(request, f"{actor.person_name} already added to movie!", extra_tags="cast")
                return redirect(request.path)

            MovieCast.objects.create(movie_name=movie, person=actor, character_name=character_name)
            return redirect(request.path)

        if 'add_language' in request.POST:
            lang_value = request.POST.get('language')
            if not lang_value:
                messages.error(request, "Please select a language.", extra_tags="lang")
                return redirect(request.path)

            lang_obj = None
            if lang_value.isdigit():
                lang_obj = Language.objects.filter(id=int(lang_value)).first()

            if not lang_obj:
                lang_obj, _ = Language.objects.get_or_create(language=lang_value)

            if MovieLanguage.objects.filter(movie_name=movie, language=lang_obj).exists():
                messages.error(request, f"{lang_obj.language} already added!", extra_tags="lang")
                return redirect(request.path)

            MovieLanguage.objects.create(movie_name=movie, language=lang_obj)
            return redirect(request.path)

        if 'done' in request.POST:
            return redirect('movies:movieDetail', movie_id=movie.id)

        return redirect(request.path)
    

class RemoveCast(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = MovieCast
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        movie_id = self.object.movie_name.id
        return reverse("movies:manage_cast_language", kwargs={"movie_id": movie_id})

class RemoveLanguage(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = MovieLanguage

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        movie_id = self.object.movie_name.id
        return reverse("movies:manage_cast_language", kwargs={"movie_id": movie_id})
    

# review
class AddEditReview(ReviewAuthorMixin, View):
    template_name = 'movies/addreview.html'

    def get(self, request, movie_id, review_id=None, *args, **kwargs):
        movie = get_object_or_404(Movie, id=movie_id)
        review = None
        if review_id:
            review = get_object_or_404(Review, id=review_id, movie_name=movie)

        context = { 
            'movie':movie,
            'review': review 
        }

        return render(request, self.template_name, context)
    
    def post(self, request, movie_id, review_id=None, *args, **kwargs):
        movie = get_object_or_404(Movie, id=movie_id)
        reviewer = request.user
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        try :
            if review_id:
                review = get_object_or_404(Review, id=review_id)
                review.rating = request.POST.get('rating')
                review.comment = request.POST.get('comment')
                review.save()
            else:
                if Review.objects.filter(movie_name=movie, user_name=reviewer).exists():
                    messages.error(request, "You have already submitted a review for this movie.")
                    return redirect('movies:movieDetail', movie_id=movie.id)
                
                review = Review.objects.create(
                movie_name=movie,
                user_name=reviewer, #add here for reviewer
                rating=rating,
                comment=comment,
                )

            avg_rating = Review.objects.filter(movie_name=movie).aggregate(Avg('rating'))['rating__avg'] or 0.0
            movie.rating = round(avg_rating, 1)
            movie.save()

            return redirect('movies:movieDetail', movie_id=movie.id)

        except Exception as e:
            messages.error(request, f"Error while adding review: {e}")

            return redirect('movies:movieDetail', movie_id=movie.id)

class DeleteReview(ReviewAuthorMixin, DeleteView):
    model = Review
    success_url = reverse_lazy("movies:genre")
    template_name = 'movies/confirmation.html'
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        movie_id = self.object.movie_name.id
        return reverse("movies:movieDetail", kwargs={"movie_id": movie_id})
    

    # Authentication

class RegistrationView(FormView):
    template_name = 'movies/registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('movies:signin')

    def form_valid(self, form):
        # form.save()
        user = form.save()
        messages.success(self.request, "Account created successfully! Please login.")
        return super().form_valid(form)

class SigninView(FormView):
    template_name = 'movies/signin.html'
    form_class = SigninForm
    success_url = reverse_lazy('movies:home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            return redirect('movies:home')
        
        if user not in Users:
            messages.error(self.request, "Account not found!")
            return redirect('movies:registration')

        # messages.error(self.request, "Invalid login credentials!")
        # return self.form_invalid(form)


    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password!")
        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

# class SignoutView(LogoutView):
#     next_page = reverse_lazy('movies:signin')
class SignoutView(View):
    def get(self, request):
        logout(request)
        return redirect('movies:signin')