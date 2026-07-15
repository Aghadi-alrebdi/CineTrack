from django.shortcuts import render
from .utils.tmdb import get_popular_movies, get_trending_tv, get_movie_details, get_movie_cast
import requests
from django.conf import settings
from tracking.models import EpisodeWatchStatus
from collections import defaultdict
from datetime import datetime, date  
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required



def home(request):
    movies = get_popular_movies(limit=20)
    shows = get_trending_tv(limit=20)

    continue_watching = []
    upcoming_episodes = []

    if request.user.is_authenticated:
        # ============================================
        # CONTINUE WATCHING
        # ============================================
        watched = (
            EpisodeWatchStatus.objects
            .filter(user=request.user, watched=True)
            .order_by("show_id", "season_number", "episode_number")
        )

        grouped = defaultdict(list)

        for ep in watched:
            grouped[ep.show_id].append(ep)

        for show_id, episodes in grouped.items():
            try:
                show = requests.get(
                    f"https://api.themoviedb.org/3/tv/{show_id}",
                    params={"api_key": settings.TMDB_API_KEY}
                ).json()
                
                total_episodes = show.get("number_of_episodes", 0)
                watched_count = len(episodes)
                
                progress = 0
                if total_episodes > 0:
                    progress = int((watched_count / total_episodes) * 100)
                
                if progress >= 100:
                    continue
                
                watched_seasons = defaultdict(list)
                for ep in episodes:
                    watched_seasons[ep.season_number].append(ep.episode_number)
                
                seasons = show.get("seasons", [])
                season_episode_counts = {}
                for season in seasons:
                    season_num = season.get("season_number", 0)
                    if season_num > 0:
                        season_episode_counts[season_num] = season.get("episode_count", 0)
                
                next_season = 1
                next_episode = 1
                found = False
                
                for season_num in sorted(season_episode_counts.keys()):
                    total_in_season = season_episode_counts.get(season_num, 0)
                    watched_in_season = watched_seasons.get(season_num, [])
                    
                    if len(watched_in_season) >= total_in_season and total_in_season > 0:
                        continue
                    else:
                        for ep_num in range(1, total_in_season + 1):
                            if ep_num not in watched_in_season:
                                next_season = season_num
                                next_episode = ep_num
                                found = True
                                break
                        if found:
                            break
                
                if not found and episodes:
                    last_ep = episodes[-1]
                    next_season = last_ep.season_number
                    next_episode = last_ep.episode_number + 1
                
                poster = show.get("poster_path", "")
                if not poster:
                    poster = show.get("backdrop_path", "")
                
                continue_watching.append({
                    "id": show_id,
                    "title": show.get("name", "Unknown Show"),
                    "poster": poster,
                    "next_season": next_season,
                    "next_episode": next_episode,
                    "progress": progress,
                    "watched_count": watched_count,
                    "total_episodes": total_episodes,
                })
            except Exception as e:
                print(f"Error processing show {show_id}: {e}")
                continue

        continue_watching.sort(key=lambda x: x['progress'], reverse=True)
        continue_watching = continue_watching[:10]

        # ============================================
        # UPCOMING EPISODES (only for shows user is watching)
        # ============================================
        upcoming_episodes = get_upcoming_episodes(request.user)

    # Create a limited version (first 4 episodes) for the initial display
    upcoming_episodes_limited = upcoming_episodes[:4] if upcoming_episodes else []

    return render(request, "dashboard/home.html", {
        "movies": movies,
        "shows": shows,
        "continue_watching": continue_watching,
        "upcoming_episodes": upcoming_episodes,
        "upcoming_episodes_limited": upcoming_episodes_limited,  # Add this
    })

def shows(request):
    """TV Shows page"""
    return render(request, 'dashboard/coming_soon.html', {
        'page_title': 'TV Shows',
        'message': 'TV Shows page is coming soon!'
    })

def movies(request):
    """Movies page"""
    return render(request, 'dashboard/coming_soon.html', {
        'page_title': 'Movies',
        'message': 'Movies page is coming soon!'
    })

def movie_detail(request, movie_id):
    movie = get_movie_details(movie_id)
    cast = get_movie_cast(movie_id)

    return render(request, "dashboard/movie_detail.html", {
        "movie": movie,
        "cast": cast[:10]  # top 10 actors
    })
from datetime import datetime  # Add this import at the top

def tv_detail(request, tv_id):
    BASE_URL = "https://api.themoviedb.org/3"
    
    # Get TV show details
    show = requests.get(
        f"{BASE_URL}/tv/{tv_id}",
        params={"api_key": settings.TMDB_API_KEY}
    ).json()
    
    # Get TV show cast
    cast_response = requests.get(
        f"{BASE_URL}/tv/{tv_id}/credits",
        params={"api_key": settings.TMDB_API_KEY}
    ).json()
    cast = cast_response.get('cast', [])
    
    seasons = show.get("seasons", [])
    
    # Load episodes for every season (skip season 0 - specials)
    for season in seasons:
        season_number = season.get("season_number", 0)
        if season_number == 0:
            season["episodes"] = []
            continue
            
        season_data = requests.get(
            f"{BASE_URL}/tv/{tv_id}/season/{season_number}",
            params={"api_key": settings.TMDB_API_KEY}
        ).json()
        season["episodes"] = season_data.get("episodes", [])
    
    # Ensure poster_path exists
    if not show.get('poster_path'):
        show['poster_path'] = show.get('backdrop_path', '')
    
    # Get current date for comparison
    now = datetime.now().date()
    
    return render(request, "dashboard/tv_detail.html", {
        "show": show,
        "seasons": seasons,
        "cast": cast[:10],
        "now": now,  # Add this to the context
    })


def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        BASE_URL = "https://api.themoviedb.org/3"
        
        search_url = f"{BASE_URL}/search/multi"
        
        params = {
            'api_key': settings.TMDB_API_KEY,
            'query': query,
            'include_adult': False,
            'language': 'en-US',
            'page': 1
        }
        
        try:
            response = requests.get(search_url, params=params)
            if response.status_code == 200:
                data = response.json()
                all_results = data.get('results', [])
                
                # Filter out people and only keep movies and TV shows
                for item in all_results:
                    if item.get('media_type') == 'person':
                        continue
                    
                    if item.get('media_type') == 'movie':
                        item['title_display'] = item.get('title', 'Unknown')
                        item['year'] = item.get('release_date', '')[:4] if item.get('release_date') else ''
                        item['link'] = f'/movies/{item.get("id")}/'
                        results.append(item)
                    elif item.get('media_type') == 'tv':
                        item['title_display'] = item.get('name', 'Unknown')
                        item['year'] = item.get('first_air_date', '')[:4] if item.get('first_air_date') else ''
                        item['link'] = f'/tv/{item.get("id")}/'
                        results.append(item)
                
                # Limit to 20 results
                results = results[:20]
                
        except requests.RequestException as e:
            print(f"API Error: {e}")
            results = []
    
    context = {
        'query': query,
        'results': results,
        'has_results': len(results) > 0,
    }
    
    return render(request, 'dashboard/search.html', context)


def continue_watching(request):
    """Page showing all shows the user has started but not finished"""
    continue_watching = []
    
    if request.user.is_authenticated:
        # Get all shows where user has watched at least one episode
        watched = (
            EpisodeWatchStatus.objects
            .filter(user=request.user, watched=True)
            .order_by("show_id", "season_number", "episode_number")
        )
        
        grouped = defaultdict(list)
        for ep in watched:
            grouped[ep.show_id].append(ep)
        
        for show_id, episodes in grouped.items():
            try:
                show = requests.get(
                    f"https://api.themoviedb.org/3/tv/{show_id}",
                    params={"api_key": settings.TMDB_API_KEY}
                ).json()
                
                total_episodes = show.get("number_of_episodes", 0)
                watched_count = len(episodes)
                
                progress = 0
                if total_episodes > 0:
                    progress = int((watched_count / total_episodes) * 100)
                
                # Only show if not 100% complete
                if progress < 100:
                    # Get next episode
                    watched_seasons = defaultdict(list)
                    for ep in episodes:
                        watched_seasons[ep.season_number].append(ep.episode_number)
                    
                    next_season = 1
                    next_episode = 1
                    
                    # Get all seasons
                    seasons = show.get("seasons", [])
                    season_episode_counts = {}
                    for season in seasons:
                        season_num = season.get("season_number", 0)
                        if season_num > 0:
                            season_episode_counts[season_num] = season.get("episode_count", 0)
                    
                    # Find next episode
                    found = False
                    for season_num in sorted(season_episode_counts.keys()):
                        total_in_season = season_episode_counts.get(season_num, 0)
                        watched_in_season = watched_seasons.get(season_num, [])
                        
                        if len(watched_in_season) >= total_in_season and total_in_season > 0:
                            continue
                        else:
                            for ep_num in range(1, total_in_season + 1):
                                if ep_num not in watched_in_season:
                                    next_season = season_num
                                    next_episode = ep_num
                                    found = True
                                    break
                            if found:
                                break
                    
                    if not found and episodes:
                        last_ep = episodes[-1]
                        next_season = last_ep.season_number
                        next_episode = last_ep.episode_number + 1
                    
                    poster = show.get("poster_path", "")
                    if not poster:
                        poster = show.get("backdrop_path", "")
                    
                    continue_watching.append({
                        "id": show_id,
                        "title": show.get("name", "Unknown Show"),
                        "poster": poster,
                        "next_season": next_season,
                        "next_episode": next_episode,
                        "progress": progress,
                        "watched_count": watched_count,
                        "total_episodes": total_episodes,
                    })
            except Exception as e:
                print(f"Error processing show {show_id}: {e}")
                continue
        
        # Sort by progress (highest first)
        continue_watching.sort(key=lambda x: x['progress'], reverse=True)
    
    return render(request, "dashboard/continue_watching.html", {
        "continue_watching": continue_watching
    })



def get_upcoming_episodes(user=None):
    """Get upcoming episodes for TV shows the user is watching (next 60 days)"""
    upcoming_episodes = []
    
    try:
        # If user is not authenticated, return empty list
        if not user or not user.is_authenticated:
            return []
        
        # Get all shows the user has watched at least one episode of
        watched_shows = EpisodeWatchStatus.objects.filter(
            user=user,
            watched=True
        ).values_list('show_id', flat=True).distinct()
        
        if not watched_shows:
            return []
        
        watched_shows = list(set(watched_shows))
        
        BASE_URL = "https://api.themoviedb.org/3"
        today = datetime.now().date()
        two_months = today + timedelta(days=60)
        
        unique_episodes_dict = {}
        
        for show_id in watched_shows:
            try:
                show_details = requests.get(
                    f"{BASE_URL}/tv/{show_id}",
                    params={"api_key": settings.TMDB_API_KEY}
                ).json()
                
                status = show_details.get('status', '')
                if status not in ['Returning Series', 'In Production', 'Planned']:
                    continue
                
                show_name = show_details.get('name', 'Unknown Show')
                poster_path = show_details.get('poster_path', '')
                
                # Get total episodes count for progress
                total_episodes = show_details.get('number_of_episodes', 0)
                
                # Get user's watched episodes for this show
                watched_episodes = EpisodeWatchStatus.objects.filter(
                    user=user,
                    show_id=show_id,
                    watched=True
                ).count()
                
                progress = 0
                if total_episodes > 0:
                    progress = int((watched_episodes / total_episodes) * 100)
                
                seasons = show_details.get('seasons', [])
                
                for season in seasons:
                    season_number = season.get('season_number', 0)
                    if season_number == 0:
                        continue
                    
                    season_data = requests.get(
                        f"{BASE_URL}/tv/{show_id}/season/{season_number}",
                        params={"api_key": settings.TMDB_API_KEY}
                    ).json()
                    
                    episodes = season_data.get('episodes', [])
                    
                    # Get user's watched episodes for this season
                    watched_in_season = EpisodeWatchStatus.objects.filter(
                        user=user,
                        show_id=show_id,
                        season_number=season_number,
                        watched=True
                    ).values_list('episode_number', flat=True)
                    
                    for episode in episodes:
                        air_date = episode.get('air_date')
                        episode_number = episode.get('episode_number', 0)
                        
                        # Skip if episode is already watched
                        if episode_number in watched_in_season:
                            continue
                        
                        if air_date:
                            try:
                                episode_date = datetime.strptime(air_date, '%Y-%m-%d').date()
                            except (ValueError, TypeError):
                                continue
                                
                            if today <= episode_date <= two_months:
                                episode_key = f"{show_id}-{season_number}-{episode_number}"
                                
                                if episode_key not in unique_episodes_dict:
                                    days_until = (episode_date - today).days
                                    
                                    # Get day name
                                    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                                    day_name = day_names[episode_date.weekday()]
                                    
                                    # Determine date label
                                    if days_until == 0:
                                        date_label = "Today"
                                    elif days_until == 1:
                                        date_label = "Tomorrow"
                                    elif days_until <= 7:
                                        date_label = day_name
                                    elif days_until <= 14:
                                        date_label = f"Next {day_name}"
                                    else:
                                        date_label = f"{day_name} ({episode_date.strftime('%b %d')})"
                                    
                                    unique_episodes_dict[episode_key] = {
                                        'show_name': show_name,
                                        'show_id': show_id,
                                        'season': season_number,
                                        'episode': episode_number,
                                        'episode_name': episode.get('name', f'Episode {episode_number}'),
                                        'air_date': air_date,
                                        'date_label': date_label,
                                        'days_until': days_until,
                                        'poster_path': poster_path,
                                        'show_status': status,
                                        'progress': progress,
                                        'total_episodes': total_episodes,
                                        'watched_episodes': watched_episodes,
                                    }
                    
            except Exception as e:
                print(f"Error processing show {show_id}: {e}")
                continue
        
        upcoming_episodes = list(unique_episodes_dict.values())
        upcoming_episodes.sort(key=lambda x: x['days_until'])
        
        return upcoming_episodes[:30]
    
    except Exception as e:
        print(f"Error fetching upcoming episodes: {e}")
        return []
    


def tv_detail(request, tv_id):
    BASE_URL = "https://api.themoviedb.org/3"
    
    # Get TV show details
    show = requests.get(
        f"{BASE_URL}/tv/{tv_id}",
        params={"api_key": settings.TMDB_API_KEY}
    ).json()
    
    # Get TV show cast
    cast_response = requests.get(
        f"{BASE_URL}/tv/{tv_id}/credits",
        params={"api_key": settings.TMDB_API_KEY}
    ).json()
    cast = cast_response.get('cast', [])
    
    seasons = show.get("seasons", [])
    
    # Load episodes for every season (skip season 0 - specials)
    for season in seasons:
        season_number = season.get("season_number", 0)
        if season_number == 0:
            season["episodes"] = []
            continue
            
        season_data = requests.get(
            f"{BASE_URL}/tv/{tv_id}/season/{season_number}",
            params={"api_key": settings.TMDB_API_KEY}
        ).json()
        season["episodes"] = season_data.get("episodes", [])
        
        # Add days_until to each episode
        today = date.today()
        for episode in season["episodes"]:
            air_date = episode.get("air_date")
            if air_date:
                try:
                    air_date_obj = datetime.strptime(air_date, '%Y-%m-%d').date()
                    days_until = (air_date_obj - today).days
                    episode["days_until"] = days_until
                except (ValueError, TypeError):
                    episode["days_until"] = None
            else:
                episode["days_until"] = None
    
    # Ensure poster_path exists
    if not show.get('poster_path'):
        show['poster_path'] = show.get('backdrop_path', '')
    
    # Get current date for comparison
    now = date.today()
    
    return render(request, "dashboard/tv_detail.html", {
        "show": show,
        "seasons": seasons,
        "cast": cast[:10],
        "now": now,
    })



from .utils.tmdb import get_popular_movies, get_trending_tv, get_movie_details, get_movie_cast, get_genres

def trending_shows(request):
    """Show all trending TV shows with genre filter"""
    genre_id = request.GET.get('genre')
    
    # Get all shows
    shows = get_trending_tv(limit=50)
    
    # Filter by genre if selected
    if genre_id and genre_id != 'all':
        genre_id = int(genre_id)
        filtered_shows = []
        for show in shows:
            # Check if the show has the selected genre
            if 'genre_ids' in show and genre_id in show.get('genre_ids', []):
                filtered_shows.append(show)
        shows = filtered_shows
    
    # Get all genres for TV shows
    genres = get_genres('tv')
    
    return render(request, "dashboard/trending_shows.html", {
        "shows": shows,
        "title": "Trending TV Shows",
        "icon": "🔥",
        "genres": genres,
        "selected_genre": genre_id,
    })

def popular_movies(request):
    """Show all popular movies with genre filter"""
    genre_id = request.GET.get('genre')
    
    # Get all movies
    movies = get_popular_movies(limit=50)
    
    # Filter by genre if selected
    if genre_id and genre_id != 'all':
        genre_id = int(genre_id)
        filtered_movies = []
        for movie in movies:
            # Check if the movie has the selected genre
            if 'genre_ids' in movie and genre_id in movie.get('genre_ids', []):
                filtered_movies.append(movie)
        movies = filtered_movies
    
    # Get all genres for movies
    genres = get_genres('movie')
    
    return render(request, "dashboard/popular_movies.html", {
        "movies": movies,
        "title": "Popular Movies",
        "icon": "🎬",
        "genres": genres,
        "selected_genre": genre_id,
    })

def all_upcoming_episodes(request):
    """Show all upcoming episodes for shows the user is watching"""
    upcoming_episodes = []
    
    if request.user.is_authenticated:
        # Use the existing function which already has the 60-day limit
        upcoming_episodes = get_upcoming_episodes(request.user)
    
    return render(request, 'dashboard/all_upcoming_episodes.html', {
        'upcoming_episodes': upcoming_episodes,
    })


