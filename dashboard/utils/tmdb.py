import requests
from django.conf import settings

BASE_URL = "https://api.themoviedb.org/3"


def get_popular_movies(limit=20):
    url = f"{BASE_URL}/movie/popular"
    
    all_results = []
    page = 1
    total_pages = 1
    
    while len(all_results) < limit and page <= total_pages:
        params = {
            "api_key": settings.TMDB_API_KEY,
            "page": page
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            # Get total pages on first request
            if page == 1:
                total_pages = data.get("total_pages", 1)
            
            all_results.extend(results)
            page += 1
            
            # If we got less than 20, we've reached the end
            if len(results) < 20:
                break
        else:
            break
    
    # Return up to the limit
    return all_results[:limit]


def get_trending_tv(limit=20):
    url = f"{BASE_URL}/trending/tv/week"
    
    all_results = []
    page = 1
    total_pages = 1
    
    while len(all_results) < limit and page <= total_pages:
        params = {
            "api_key": settings.TMDB_API_KEY,
            "page": page
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            # Get total pages on first request
            if page == 1:
                total_pages = data.get("total_pages", 1)
            
            all_results.extend(results)
            page += 1
            
            # If we got less than 20, we've reached the end
            if len(results) < 20:
                break
        else:
            break
    
    # Return up to the limit
    return all_results[:limit]


def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"

    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US"
    }

    return requests.get(url, params=params).json()


def get_movie_cast(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/credits"

    params = {
        "api_key": settings.TMDB_API_KEY
    }

    data = requests.get(url, params=params).json()
    return data.get("cast", [])




def tv_detail(request, tv_id):
    show = get_tv_details(tv_id)
    seasons = show.get("seasons", [])

    return render(request, "dashboard/tv_detail.html", {
        "show": show,
        "seasons": seasons
    })


def get_season(tv_id, season_number):
    url = f"{BASE_URL}/tv/{tv_id}/season/{season_number}"

    params = {
        "api_key": settings.TMDB_API_KEY
    }

    return requests.get(url, params=params).json()

def get_genres(media_type='movie'):
    """Get all genres for movies or TV shows from TMDB"""
    url = f"{BASE_URL}/genre/{media_type}/list"
    
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US"
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("genres", [])
    return []