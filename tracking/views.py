from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import WatchHistory, EpisodeWatchStatus, Comment
from .forms import CommentForm
import json
import requests
from django.conf import settings


@login_required
@csrf_exempt
def toggle_watchlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            media_id = data.get('media_id')
            media_type = data.get('media_type')
            title = data.get('title')
            poster_path = data.get('poster_path', '')
            
            print(f"📺 TOGGLE WATCHLIST - User: {request.user.username}")
            print(f"   Media ID: {media_id}, Type: {media_type}")
            print(f"   Poster Path: {poster_path}")
            
            # If poster_path is empty, try to fetch it from TMDB
            if not poster_path:
                BASE_URL = "https://api.themoviedb.org/3"
                if media_type == 'tv':
                    url = f"{BASE_URL}/tv/{media_id}"
                else:
                    url = f"{BASE_URL}/movie/{media_id}"
                    
                response = requests.get(url, params={"api_key": settings.TMDB_API_KEY})
                if response.status_code == 200:
                    data = response.json()
                    poster_path = data.get('poster_path', '')
                    if not poster_path:
                        poster_path = data.get('backdrop_path', '')
                    print(f"   Fetched poster from TMDB: {poster_path}")
            
            watch_entry, created = WatchHistory.objects.get_or_create(
                user=request.user,
                media_id=media_id,
                media_type=media_type,
                defaults={
                    'title': title,
                    'poster_path': poster_path,
                }
            )
            
            # If entry exists but poster is empty, update it
            if not created and not watch_entry.poster_path and poster_path:
                watch_entry.poster_path = poster_path
            
            watch_entry.watchlist = not watch_entry.watchlist
            watch_entry.save()
            
            print(f"   ✅ Watchlist toggled to: {watch_entry.watchlist}")
            
            return JsonResponse({
                'success': True,
                'in_watchlist': watch_entry.watchlist,
                'message': 'Added to watchlist' if watch_entry.watchlist else 'Removed from watchlist'
            })
        except Exception as e:
            print(f"❌ Error in toggle_watchlist: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@csrf_exempt
def toggle_watched_movie(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            media_id = data.get('media_id')
            title = data.get('title')
            poster_path = data.get('poster_path', '')
            
            if not poster_path:
                response = requests.get(
                    f"https://api.themoviedb.org/3/movie/{media_id}",
                    params={"api_key": settings.TMDB_API_KEY}
                )
                if response.status_code == 200:
                    data = response.json()
                    poster_path = data.get('poster_path', '')
            
            watch_entry, created = WatchHistory.objects.get_or_create(
                user=request.user,
                media_id=media_id,
                media_type='movie',
                defaults={
                    'title': title,
                    'poster_path': poster_path,
                }
            )
            
            if not created and not watch_entry.poster_path and poster_path:
                watch_entry.poster_path = poster_path
            
            watch_entry.watched = not watch_entry.watched
            watch_entry.save()
            
            return JsonResponse({
                'success': True,
                'watched': watch_entry.watched,
                'message': 'Marked as watched' if watch_entry.watched else 'Marked as unwatched'
            })
        except Exception as e:
            print(f"Error in toggle_watched_movie: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@csrf_exempt
def toggle_episode_watched(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"📺 EPISODE WATCH - Received data:")
            print(json.dumps(data, indent=2))
            
            show_id = data.get('show_id')
            show_title = data.get('show_title')
            poster_path = data.get('poster_path', '')
            season_number = data.get('season_number')
            episode_number = data.get('episode_number')
            episode_title = data.get('episode_title', '')
            
            if not all([show_id, season_number, episode_number]):
                return JsonResponse({
                    'success': False, 
                    'error': 'Missing required fields'
                })
            
            print(f"📺 User: {request.user.username}")
            print(f"   Show ID: {show_id}, Title: {show_title}")
            print(f"   Poster Path from request: {poster_path}")
            
            # If poster_path is empty, try to fetch it from TMDB
            if not poster_path:
                print("   ⚠️ Poster path is empty, fetching from TMDB...")
                try:
                    response = requests.get(
                        f"https://api.themoviedb.org/3/tv/{show_id}",
                        params={"api_key": settings.TMDB_API_KEY}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        poster_path = data.get('poster_path', '')
                        if not poster_path:
                            poster_path = data.get('backdrop_path', '')
                        print(f"   ✅ Fetched poster from TMDB: {poster_path}")
                except Exception as e:
                    print(f"   ❌ Error fetching poster: {e}")
            
            # Get or create episode status
            episode_status, created = EpisodeWatchStatus.objects.get_or_create(
                user=request.user,
                show_id=show_id,
                season_number=season_number,
                episode_number=episode_number,
                defaults={
                    'show_title': show_title or 'Unknown Show',
                    'episode_title': episode_title or f'Episode {episode_number}',
                }
            )
            
            episode_status.watched = not episode_status.watched
            episode_status.save()
            
            print(f"   Episode watched status: {episode_status.watched}")
            
            # ALWAYS add/update the show in WatchHistory with poster
            watch_entry, created = WatchHistory.objects.get_or_create(
                user=request.user,
                media_id=show_id,
                media_type='tv',
                defaults={
                    'title': show_title or 'Unknown Show',
                    'poster_path': poster_path,
                }
            )
            
            print(f"   WatchHistory entry created: {created}")
            
            # Update poster if it's empty
            if not watch_entry.poster_path and poster_path:
                watch_entry.poster_path = poster_path
                print(f"   ✅ Updated poster in WatchHistory: {poster_path}")
            
            # Check if any episodes are watched for this show
            any_episode_watched = EpisodeWatchStatus.objects.filter(
                user=request.user,
                show_id=show_id,
                watched=True
            ).exists()
            
            # Update watched status based on episodes
            watch_entry.watched = any_episode_watched
            watch_entry.save()
            
            print(f"   📺 Show watched status: {watch_entry.watched}")
            print(f"   📺 Poster saved: {watch_entry.poster_path}")
            
            return JsonResponse({
                'success': True,
                'watched': episode_status.watched,
                'message': 'Episode marked as watched' if episode_status.watched else 'Episode marked as unwatched'
            })
        except Exception as e:
            print(f"❌ Error in toggle_episode_watched: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@csrf_exempt
def toggle_season_watched(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"📺 SEASON WATCH - Received data:")
            print(json.dumps(data, indent=2))
            
            show_id = data.get('show_id')
            show_title = data.get('show_title')
            poster_path = data.get('poster_path', '')
            season_number = data.get('season_number')
            episodes = data.get('episodes', [])
            
            if not all([show_id, season_number]):
                return JsonResponse({
                    'success': False, 
                    'error': 'Missing required fields'
                })
            
            # If poster_path is empty, try to fetch it from TMDB
            if not poster_path:
                try:
                    response = requests.get(
                        f"https://api.themoviedb.org/3/tv/{show_id}",
                        params={"api_key": settings.TMDB_API_KEY}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        poster_path = data.get('poster_path', '')
                        if not poster_path:
                            poster_path = data.get('backdrop_path', '')
                except Exception as e:
                    print(f"   ❌ Error fetching poster: {e}")
            
            # Get all episodes in this season
            episode_statuses = EpisodeWatchStatus.objects.filter(
                user=request.user,
                show_id=show_id,
                season_number=season_number
            )
            
            # Check if all episodes are already watched
            if episode_statuses.exists():
                all_watched = all(ep.watched for ep in episode_statuses)
            else:
                all_watched = False
            
            if all_watched:
                # Unwatch all
                episode_statuses.update(watched=False)
                watched_status = False
                message = 'Season marked as unwatched'
            else:
                # Watch all - create any missing episodes first
                for ep in episodes:
                    episode_status, created = EpisodeWatchStatus.objects.get_or_create(
                        user=request.user,
                        show_id=show_id,
                        season_number=season_number,
                        episode_number=ep['episode_number'],
                        defaults={
                            'show_title': show_title or 'Unknown Show',
                            'episode_title': ep.get('name', f'Episode {ep["episode_number"]}'),
                        }
                    )
                    episode_status.watched = True
                    episode_status.save()
                watched_status = True
                message = 'Season marked as watched'
            
            # ALWAYS add/update the show in WatchHistory with poster
            watch_entry, created = WatchHistory.objects.get_or_create(
                user=request.user,
                media_id=show_id,
                media_type='tv',
                defaults={
                    'title': show_title or 'Unknown Show',
                    'poster_path': poster_path,
                }
            )
            
            # Update poster if it's empty
            if not watch_entry.poster_path and poster_path:
                watch_entry.poster_path = poster_path
            
            # Check if any episodes are watched for this show
            any_episode_watched = EpisodeWatchStatus.objects.filter(
                user=request.user,
                show_id=show_id,
                watched=True
            ).exists()
            
            # Update watched status based on episodes
            watch_entry.watched = any_episode_watched
            watch_entry.save()
            
            return JsonResponse({
                'success': True,
                'all_watched': watched_status,
                'message': message
            })
        except Exception as e:
            print(f"❌ Error in toggle_season_watched: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# ==============================
# TOGGLE SHOW WATCHED (Mark whole show as watched/unwatched)
# ==============================
@login_required
@csrf_exempt
def toggle_show_watched(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"📺 TOGGLE SHOW WATCHED - Received data:")
            print(json.dumps(data, indent=2))
            
            show_id = data.get('show_id')
            show_title = data.get('show_title')
            poster_path = data.get('poster_path', '')
            total_episodes = data.get('total_episodes', 0)
            watched = data.get('watched', True)
            
            if not show_id:
                return JsonResponse({
                    'success': False, 
                    'error': 'Missing show_id'
                })
            
            # If poster_path is empty, try to fetch it from TMDB
            if not poster_path:
                try:
                    response = requests.get(
                        f"https://api.themoviedb.org/3/tv/{show_id}",
                        params={"api_key": settings.TMDB_API_KEY}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        poster_path = data.get('poster_path', '')
                        if not poster_path:
                            poster_path = data.get('backdrop_path', '')
                        print(f"   Fetched poster from TMDB: {poster_path}")
                except Exception as e:
                    print(f"   ❌ Error fetching poster: {e}")
            
            # Get or create WatchHistory entry
            watch_entry, created = WatchHistory.objects.get_or_create(
                user=request.user,
                media_id=show_id,
                media_type='tv',
                defaults={
                    'title': show_title or 'Unknown Show',
                    'poster_path': poster_path,
                }
            )
            
            # Update poster if empty
            if not watch_entry.poster_path and poster_path:
                watch_entry.poster_path = poster_path
            
            # Mark the whole show as watched/unwatched
            watch_entry.watched = watched
            watch_entry.save()
            
            # If marking as watched, mark all episodes as watched
            if watched:
                print("   📺 Marking all episodes as watched...")
                BASE_URL = "https://api.themoviedb.org/3"
                
                # Get show details to get all seasons
                show_data = requests.get(
                    f"{BASE_URL}/tv/{show_id}",
                    params={"api_key": settings.TMDB_API_KEY}
                ).json()
                
                seasons = show_data.get('seasons', [])
                
                for season in seasons:
                    season_number = season.get('season_number', 0)
                    if season_number == 0:
                        continue
                    
                    # Get episodes for this season
                    season_data = requests.get(
                        f"{BASE_URL}/tv/{show_id}/season/{season_number}",
                        params={"api_key": settings.TMDB_API_KEY}
                    ).json()
                    
                    episodes = season_data.get('episodes', [])
                    
                    for ep in episodes:
                        # Mark each episode as watched
                        episode_status, created = EpisodeWatchStatus.objects.get_or_create(
                            user=request.user,
                            show_id=show_id,
                            season_number=season_number,
                            episode_number=ep.get('episode_number'),
                            defaults={
                                'show_title': show_title or 'Unknown Show',
                                'episode_title': ep.get('name', f'Episode {ep.get("episode_number")}'),
                            }
                        )
                        episode_status.watched = True
                        episode_status.save()
                
                print(f"   ✅ All episodes marked as watched")
            else:
                # If marking as unwatched, mark all episodes as unwatched
                print("   📺 Marking all episodes as unwatched...")
                EpisodeWatchStatus.objects.filter(
                    user=request.user,
                    show_id=show_id
                ).update(watched=False)
                print(f"   ✅ All episodes marked as unwatched")
            
            print(f"✅ Show {show_title} marked as {'watched' if watched else 'unwatched'}")
            
            return JsonResponse({
                'success': True,
                'watched': watch_entry.watched,
                'message': f'Show marked as {("watched" if watch_entry.watched else "unwatched")}'
            })
        except Exception as e:
            print(f"❌ Error in toggle_show_watched: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_user_status(request):
    """Get the current status of a media item for the logged-in user"""
    media_id = request.GET.get('media_id')
    media_type = request.GET.get('media_type')
    
    if not media_id or not media_type:
        return JsonResponse({'success': False, 'error': 'Missing parameters'})
    
    try:
        watch_entry = WatchHistory.objects.get(
            user=request.user,
            media_id=media_id,
            media_type=media_type
        )
        data = {
            'success': True,
            'watchlist': watch_entry.watchlist,
            'watched': watch_entry.watched,
            'rating': watch_entry.rating,
        }
    except WatchHistory.DoesNotExist:
        data = {
            'success': True,
            'watchlist': False,
            'watched': False,
            'rating': None,
        }
    
    return JsonResponse(data)

@login_required
def get_poster(request):
    """Get poster path for a media item"""
    media_id = request.GET.get('media_id')
    media_type = request.GET.get('media_type')
    
    if not media_id or not media_type:
        return JsonResponse({'success': False, 'error': 'Missing parameters'})
    
    try:
        BASE_URL = "https://api.themoviedb.org/3"
        
        if media_type == 'tv':
            url = f"{BASE_URL}/tv/{media_id}"
        else:
            url = f"{BASE_URL}/movie/{media_id}"
        
        response = requests.get(url, params={"api_key": settings.TMDB_API_KEY})
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get('poster_path', '')
            if not poster_path:
                poster_path = data.get('backdrop_path', '')
            return JsonResponse({'success': True, 'poster_path': poster_path})
        else:
            return JsonResponse({'success': False, 'error': 'TMDB API error'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
    

@login_required
def get_episode_status(request):
    """Get the status of a specific episode for the logged-in user"""
    show_id = request.GET.get('show_id')
    season_number = request.GET.get('season_number')
    episode_number = request.GET.get('episode_number')
    
    if not all([show_id, season_number, episode_number]):
        return JsonResponse({'success': False, 'error': 'Missing parameters'})
    
    try:
        episode_status = EpisodeWatchStatus.objects.get(
            user=request.user,
            show_id=show_id,
            season_number=season_number,
            episode_number=episode_number
        )
        data = {
            'success': True,
            'watched': episode_status.watched,
        }
    except EpisodeWatchStatus.DoesNotExist:
        data = {
            'success': True,
            'watched': False,
        }
    
    return JsonResponse(data)


@login_required
def get_season_status(request):
    """Get the status of a specific season for the logged-in user"""
    show_id = request.GET.get('show_id')
    season_number = request.GET.get('season_number')
    
    if not all([show_id, season_number]):
        return JsonResponse({'success': False, 'error': 'Missing parameters'})
    
    try:
        # Get all episodes in this season
        episodes = EpisodeWatchStatus.objects.filter(
            user=request.user,
            show_id=show_id,
            season_number=season_number
        )
        
        if episodes.exists():
            all_watched = all(ep.watched for ep in episodes)
            data = {
                'success': True,
                'watched': all_watched,
                'total_episodes': episodes.count(),
                'watched_episodes': episodes.filter(watched=True).count(),
            }
        else:
            data = {
                'success': True,
                'watched': False,
                'total_episodes': 0,
                'watched_episodes': 0,
            }
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse(data)



@login_required
@csrf_exempt
def rate_media(request):
    """Rate a movie or TV show"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"⭐ RATING - Received data: {data}")
            
            media_id = data.get('media_id')
            media_type = data.get('media_type')
            rating = data.get('rating')
            title = data.get('title', 'Unknown')
            poster_path = data.get('poster_path', '')
            
            if not all([media_id, media_type, rating is not None]):
                return JsonResponse({
                    'success': False, 
                    'error': 'Missing required fields'
                })
            
            # Validate rating (1-10)
            try:
                rating = int(rating)
                if rating < 1 or rating > 10:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Rating must be between 1 and 10'
                    })
            except ValueError:
                return JsonResponse({
                    'success': False, 
                    'error': 'Rating must be a number'
                })
            
            # Get or create WatchHistory entry
            watch_entry, created = WatchHistory.objects.get_or_create(
                user=request.user,
                media_id=media_id,
                media_type=media_type,
                defaults={
                    'title': title,
                    'poster_path': poster_path,
                }
            )
            
            # Update rating
            watch_entry.rating = rating
            watch_entry.save()
            
            print(f"✅ Rating saved for {media_type} {media_id}: {rating}/10")
            
            return JsonResponse({
                'success': True,
                'rating': watch_entry.rating,
                'message': f'Rated {rating}/10'
            })
        except Exception as e:
            print(f"❌ Error in rate_media: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_rating(request):
    """Get user's rating for a media item"""
    media_id = request.GET.get('media_id')
    media_type = request.GET.get('media_type')
    
    if not media_id or not media_type:
        return JsonResponse({'success': False, 'error': 'Missing parameters'})
    
    try:
        watch_entry = WatchHistory.objects.get(
            user=request.user,
            media_id=media_id,
            media_type=media_type
        )
        return JsonResponse({
            'success': True,
            'rating': watch_entry.rating,
        })
    except WatchHistory.DoesNotExist:
        return JsonResponse({
            'success': True,
            'rating': None,
        })
    

    
@login_required
def add_comment(request, media_id, media_type):
    """Add a comment to a movie or TV show"""
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.media_id = media_id
            comment.media_type = media_type
            
            # Get media title from TMDB
            try:
                BASE_URL = "https://api.themoviedb.org/3"
                if media_type == 'tv':
                    url = f"{BASE_URL}/tv/{media_id}"
                else:
                    url = f"{BASE_URL}/movie/{media_id}"
                response = requests.get(url, params={"api_key": settings.TMDB_API_KEY})
                if response.status_code == 200:
                    data = response.json()
                    comment.media_title = data.get('name') or data.get('title', 'Unknown')
                else:
                    comment.media_title = 'Unknown'
            except:
                comment.media_title = 'Unknown'
            
            comment.save()
            
            # Redirect back to the same page
            if media_type == 'tv':
                return redirect('tv_detail', tv_id=media_id)
            else:
                return redirect('movie_detail', movie_id=media_id)
    
    # If not POST, redirect to detail page
    if media_type == 'tv':
        return redirect('tv_detail', tv_id=media_id)
    else:
        return redirect('movie_detail', movie_id=media_id)

def get_comments(request, media_id, media_type):
    """Get all comments for a media item"""
    comments = Comment.objects.filter(
        media_id=media_id,
        media_type=media_type
    ).select_related('user')
    
    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'username': comment.user.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'is_owner': request.user.is_authenticated and request.user == comment.user,
        })
    
    return JsonResponse({'success': True, 'comments': comments_data})

@login_required
def delete_comment(request, comment_id):
    """Delete a comment (only if user owns it)"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user != comment.user:
        return JsonResponse({'success': False, 'error': 'You cannot delete this comment'})
    
    media_id = comment.media_id
    media_type = comment.media_type
    
    comment.delete()
    
    return JsonResponse({'success': True, 'message': 'Comment deleted'})