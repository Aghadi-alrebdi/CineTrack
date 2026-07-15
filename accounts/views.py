from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm
from tracking.models import WatchHistory, EpisodeWatchStatus
from .models import Profile, Follow
import requests
from django.conf import settings

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')
@login_required
def profile(request, username=None):
    # If no username provided, show current user's profile
    if username is None:
        user = request.user
    else:
        user = get_object_or_404(User, username=username)
    
    # Check if this is the current user's own profile
    is_owner = request.user == user
    
    # Check if current user follows this profile
    is_following = False
    if request.user.is_authenticated and not is_owner:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    
    if request.method == 'POST' and is_owner:
        # Check if it's a bio-only update
        if 'update_bio' in request.POST:
            bio = request.POST.get('bio', '')
            profile = request.user.profile
            profile.bio = bio
            profile.save()
            messages.success(request, 'Bio updated successfully!')
            return redirect('profile', username=request.user.username)
        
        # Regular profile update (username, email, picture, etc.)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=user.profile)
    
    # Get user's stats
    watchlist_count = WatchHistory.objects.filter(user=user, watchlist=True).count()
    watched_count = WatchHistory.objects.filter(user=user, watched=True).count()
    episodes_watched = EpisodeWatchStatus.objects.filter(user=user, watched=True).count()
    
    # Get followers and following counts
    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    
    # Get watched movies (fully watched)
    watched_movies = WatchHistory.objects.filter(
        user=user,
        media_type='movie',
        watched=True
    ).order_by('-date_updated')[:12]
    
    # Get watched TV shows (fully watched)
    watched_tv_shows = WatchHistory.objects.filter(
        user=user,
        media_type='tv',
        watched=True
    ).order_by('-date_updated')[:12]
    
    # Combine and format watched items
    watched_items = []
    
    for movie in watched_movies:
        watched_items.append({
            'id': movie.media_id,
            'title': movie.title,
            'poster_path': movie.poster_path,
            'media_type': 'movie',
            'rating': movie.rating,
        })
    
    for show in watched_tv_shows:
        watched_items.append({
            'id': show.media_id,
            'title': show.title,
            'poster_path': show.poster_path,
            'media_type': 'tv',
            'rating': show.rating,
        })
    
    context = {
        'profile_user': user,
        'is_owner': is_owner,
        'is_following': is_following,
        'u_form': u_form,
        'p_form': p_form,
        'watchlist_count': watchlist_count,
        'watched_count': watched_count,
        'episodes_watched': episodes_watched,
        'followers_count': followers_count,
        'following_count': following_count,
        'watched_items': watched_items,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_watched_all(request, username):
    """Show all watched items of a user"""
    user = get_object_or_404(User, username=username)
    
    # Get all watched movies
    movies = WatchHistory.objects.filter(
        user=user,
        media_type='movie',
        watched=True
    ).order_by('-date_updated')
    
    # Get all watched TV shows
    tv_shows = WatchHistory.objects.filter(
        user=user,
        media_type='tv',
        watched=True
    ).order_by('-date_updated')
    
    watched_items = []
    
    for movie in movies:
        watched_items.append({
            'id': movie.media_id,
            'title': movie.title,
            'poster_path': movie.poster_path,
            'media_type': 'movie',
            'rating': movie.rating,
        })
    
    for show in tv_shows:
        watched_items.append({
            'id': show.media_id,
            'title': show.title,
            'poster_path': show.poster_path,
            'media_type': 'tv',
            'rating': show.rating,
        })
    
    return render(request, 'accounts/profile_watched_all.html', {
        'profile_user': user,
        'watched_items': watched_items,
        'is_owner': request.user == user,
    })


@login_required
def follow_user(request, username):
    """Follow a user"""
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user == user_to_follow:
        messages.error(request, "You cannot follow yourself.")
        return redirect('profile', username=username)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if created:
        messages.success(request, f"You are now following {username}!")
    else:
        messages.info(request, f"You already follow {username}.")
    
    return redirect('profile', username=username)

@login_required
def unfollow_user(request, username):
    """Unfollow a user"""
    user_to_unfollow = get_object_or_404(User, username=username)
    
    Follow.objects.filter(
        follower=request.user,
        following=user_to_unfollow
    ).delete()
    
    messages.success(request, f"You have unfollowed {username}.")
    return redirect('profile', username=username)

@login_required
def followers_list(request, username):
    """View all followers of a user"""
    user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=user).select_related('follower')
    
    # Check if current user follows each follower
    for follow in followers:
        follow.is_following = Follow.objects.filter(
            follower=request.user,
            following=follow.follower
        ).exists()
    
    return render(request, 'accounts/followers_list.html', {
        'profile_user': user,
        'followers': followers,
        'is_owner': request.user == user,
    })

@login_required
def following_list(request, username):
    """View all users a user is following"""
    user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=user).select_related('following')
    
    # Check if current user follows each person
    for follow in following:
        follow.is_following = Follow.objects.filter(
            follower=request.user,
            following=follow.following
        ).exists()
    
    return render(request, 'accounts/following_list.html', {
        'profile_user': user,
        'following': following,
        'is_owner': request.user == user,
    })

def watchlist_view(request):
    if request.user.is_authenticated:
        watchlist_items = WatchHistory.objects.filter(user=request.user, watchlist=True)
    else:
        watchlist_items = []
    return render(request, 'accounts/watchlist.html', {'watchlist': watchlist_items})

@login_required
def watched_view(request):
    """Show only fully completed movies and TV shows"""
    if not request.user.is_authenticated:
        return render(request, 'accounts/watched.html', {'watched': []})
    
    watched_items = []
    
    # 1. Get all watched movies (fully watched)
    movies = WatchHistory.objects.filter(
        user=request.user,
        media_type='movie',
        watched=True
    )
    
    for movie in movies:
        watched_items.append({
            'id': movie.media_id,
            'title': movie.title,
            'poster_path': movie.poster_path,
            'media_type': 'movie',
            'watched': movie.watched,
            'watchlist': movie.watchlist,
            'rating': movie.rating,
            'is_completed': True,
        })
    
    # 2. Get all TV shows that are fully watched
    tv_shows = WatchHistory.objects.filter(
        user=request.user,
        media_type='tv',
        watched=True
    )
    
    for show in tv_shows:
        show_id = show.media_id
        show_title = show.title
        
        try:
            response = requests.get(
                f"https://api.themoviedb.org/3/tv/{show_id}",
                params={"api_key": settings.TMDB_API_KEY}
            )
            if response.status_code == 200:
                show_data = response.json()
                total_episodes = show_data.get('number_of_episodes', 0)
                
                watched_count = EpisodeWatchStatus.objects.filter(
                    user=request.user,
                    show_id=show_id,
                    watched=True
                ).count()
                
                if total_episodes > 0 and watched_count >= total_episodes:
                    watched_items.append({
                        'id': show_id,
                        'title': show_title,
                        'poster_path': show.poster_path or show_data.get('poster_path', ''),
                        'media_type': 'tv',
                        'watched': show.watched,
                        'watchlist': show.watchlist,
                        'rating': show.rating,
                        'is_completed': True,
                        'total_episodes': total_episodes,
                        'watched_episodes': watched_count,
                    })
                else:
                    if show.watched:
                        show.watched = False
                        show.save()
        except Exception as e:
            print(f"Error processing show {show_id}: {e}")
            continue
    
    watched_items.sort(key=lambda x: x['title'])
    
    return render(request, 'accounts/watched.html', {'watched': watched_items})

def search_users(request):
    """Search for users"""
    query = request.GET.get('q', '').strip()
    users = []
    
    if query and request.user.is_authenticated:
        # Search for users by username (case insensitive)
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=request.user.id).distinct()[:20]  # Exclude current user
        
        # Get the IDs of users the current user is following
        following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
        
        # Add follow status to each user
        for user in users:
            user.is_following = user.id in following_ids
    
    return render(request, 'accounts/search_users.html', {
        'query': query,
        'users': users,
    })


@login_required
def delete_account(request):
    """Delete the user's account"""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')
    
    return render(request, 'accounts/delete_account_confirm.html')