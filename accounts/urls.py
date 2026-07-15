from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/watched/', views.profile_watched_all, name='profile_watched'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('followers/<str:username>/', views.followers_list, name='followers_list'),
    path('following/<str:username>/', views.following_list, name='following_list'),
    path('search/', views.search_users, name='search_users'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('watched/', views.watched_view, name='watched'),
    path('delete-account/', views.delete_account, name='delete_account'),

]