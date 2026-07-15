from django.urls import path
from . import views

urlpatterns = [
    path('api/toggle-watchlist/', views.toggle_watchlist, name='toggle_watchlist'),
    path('api/toggle-watched-movie/', views.toggle_watched_movie, name='toggle_watched_movie'),
    path('api/toggle-episode-watched/', views.toggle_episode_watched, name='toggle_episode_watched'),
    path('api/toggle-season-watched/', views.toggle_season_watched, name='toggle_season_watched'),
    path('api/get-user-status/', views.get_user_status, name='get_user_status'),
    path('api/get-poster/', views.get_poster, name='get_poster'),

    path('api/toggle-show-watched/', views.toggle_show_watched, name='toggle_show_watched'),  
    path('api/get-episode-status/', views.get_episode_status, name='get_episode_status'),  
    path('api/get-season-status/', views.get_season_status, name='get_season_status'),  


    path('api/rate-media/', views.rate_media, name='rate_media'),  # NEW
    path('api/get-rating/', views.get_rating, name='get_rating'),  # NEW

     path('comment/add/<int:media_id>/<str:media_type>/', views.add_comment, name='add_comment'),
    path('comment/get/<int:media_id>/<str:media_type>/', views.get_comments, name='get_comments'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]