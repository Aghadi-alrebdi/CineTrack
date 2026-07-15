// ==============================
// EPISODE WATCH BUTTON TOGGLE
// ==============================
function toggleWatch(button) {
    event.stopPropagation();
    
    const showId = button.dataset.showId;
    const showTitle = button.dataset.showTitle;
    const posterPath = button.dataset.posterPath;
    const seasonNumber = button.dataset.seasonNumber;
    const episodeNumber = button.dataset.episodeNumber;
    const episodeTitle = button.dataset.episodeTitle;
    
    if (!showId || !seasonNumber || !episodeNumber) {
        console.error('Missing episode data');
        return;
    }
    
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    button.disabled = true;
    
    fetch('/tracking/api/toggle-episode-watched/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            show_id: showId,
            show_title: showTitle,
            poster_path: posterPath,
            season_number: seasonNumber,
            episode_number: episodeNumber,
            episode_title: episodeTitle,
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.watched) {
                button.classList.add('watched');
                button.textContent = 'Watched';
            } else {
                button.classList.remove('watched');
                button.textContent = 'Watch';
            }
            updateShowWatchedStatus(showId);
        } else {
            console.error('Error:', data.error);
            button.textContent = originalText;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        button.textContent = originalText;
    })
    .finally(() => {
        button.disabled = false;
    });
}

// ==============================
// SEASON WATCH BUTTON TOGGLE
// ==============================
function toggleSeasonWatched(button, seasonId) {
    event.stopPropagation();
    
    const showId = button.dataset.showId;
    const showTitle = button.dataset.showTitle;
    const posterPath = button.dataset.posterPath;
    const seasonNumber = button.dataset.seasonNumber;

    if (!showId || !seasonNumber) {
        console.error('Missing season data');
        return;
    }
    
    const seasonContainer = document.getElementById(seasonId);
    if (!seasonContainer) {
        console.error('Season container not found:', seasonId);
        return;
    }
    
    const episodes = [];
    const episodeButtons = seasonContainer.querySelectorAll('.episode-watch-btn');
    
    episodeButtons.forEach(btn => {
        episodes.push({
            episode_number: parseInt(btn.dataset.episodeNumber),
            name: btn.dataset.episodeTitle || `Episode ${btn.dataset.episodeNumber}`
        });
    });
    
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    button.disabled = true;
    
    fetch('/tracking/api/toggle-season-watched/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            show_id: showId,
            show_title: showTitle,
            poster_path: posterPath,
            season_number: seasonNumber,
            episodes: episodes,
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.all_watched) {
                episodeButtons.forEach(btn => {
                    btn.classList.add('watched');
                    btn.textContent = 'Watched';
                });
                button.classList.add('season-watched');
                button.textContent = 'Season Watched';
            } else {
                episodeButtons.forEach(btn => {
                    btn.classList.remove('watched');
                    btn.textContent = 'Watch';
                });
                button.classList.remove('season-watched');
                button.textContent = 'Mark Season';
            }
            updateShowWatchedStatus(showId);
        } else {
            console.error('Error:', data.error);
            button.textContent = originalText;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        button.textContent = originalText;
    })
    .finally(() => {
        button.disabled = false;
    });
}