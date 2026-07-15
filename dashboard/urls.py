
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
     path("tv/<int:tv_id>/", views.tv_detail, name="tv_detail"),

    path('search/', views.search, name='search'),
     path('continue-watching/', views.continue_watching, name='continue_watching'), 

         path('trending-shows/', views.trending_shows, name='trending_shows'),  # Add this
    path('popular-movies/', views.popular_movies, name='popular_movies'),  # Add this
        path('upcoming-episodes/', views.all_upcoming_episodes, name='all_upcoming_episodes'),

 

]