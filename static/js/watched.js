// ==============================
// WATCHED BUTTON TOGGLE for MOVIES
// ==============================
function toggleWatched(button) {
    const mediaId = button.dataset.mediaId;
    const title = button.dataset.title;
    const posterPath = button.dataset.posterPath;
    
    if (!mediaId) {
        console.error('Missing media data');
        return;
    }
    
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    button.disabled = true;
    
    fetch('/tracking/api/toggle-watched-movie/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            media_id: mediaId,
            title: title,
            poster_path: posterPath,
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.watched) {
                button.classList.add('watched');
                button.textContent = 'Watched ✓';
            } else {
                button.classList.remove('watched');
                button.textContent = 'Mark as Watched';
            }
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
// WATCHED BUTTON TOGGLE for TV SHOWS (Original working version)
// ==============================
function toggleShowWatched(button) {
    const showId = button.dataset.showId;
    const showTitle = button.dataset.showTitle;
    const posterPath = button.dataset.posterPath || '';
    const totalEpisodes = parseInt(button.dataset.totalEpisodes) || 0;
    
    if (!showId) {
        console.error('Missing show data');
        return;
    }
    
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    button.disabled = true;
    
    const isWatched = button.classList.contains('watched');
    
    fetch('/tracking/api/toggle-show-watched/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            show_id: showId,
            show_title: showTitle,
            poster_path: posterPath,
            total_episodes: totalEpisodes,
            watched: !isWatched,
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.watched) {
                button.classList.add('watched');
                button.textContent = 'Watched ✓';
            } else {
                button.classList.remove('watched');
                button.textContent = 'Mark as Watched';
            }
            
            const allEpisodeBtns = document.querySelectorAll(`.episode-watch-btn[data-show-id="${showId}"]`);
            allEpisodeBtns.forEach(epBtn => {
                if (data.watched) {
                    epBtn.classList.add('watched');
                    epBtn.textContent = 'Watched';
                } else {
                    epBtn.classList.remove('watched');
                    epBtn.textContent = 'Watch';
                }
            });
            
            const allSeasonBtns = document.querySelectorAll(`.season-watch-btn[data-show-id="${showId}"]`);
            allSeasonBtns.forEach(seasonBtn => {
                if (data.watched) {
                    seasonBtn.classList.add('season-watched');
                    seasonBtn.textContent = 'Season Watched';
                } else {
                    seasonBtn.classList.remove('season-watched');
                    seasonBtn.textContent = 'Mark Season';
                }
            });
        } else {
            console.error('Error:', data.error);
            button.textContent = originalText;
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        button.textContent = originalText;
        alert('Network error: ' + error);
    })
    .finally(() => {
        button.disabled = false;
    });
}