// ==============================
// HELPER: Get CSRF Token
// ==============================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ==============================
// SEASON TOGGLE with arrow rotation
// ==============================
function toggleSeason(id, element) {
    const section = document.getElementById(id);
    const arrow = element.querySelector('.arrow');
    
    if (section) {
        section.classList.toggle('d-none');
        if (arrow) {
            arrow.classList.toggle('rotated');
        }
    }
}

// ==============================
// UPDATE SHOW WATCHED STATUS
// ==============================
function updateShowWatchedStatus(showId) {
    const seasonBtns = document.querySelectorAll(`.season-watch-btn[data-show-id="${showId}"]`);
    if (seasonBtns.length === 0) return;
    
    let allSeasonsWatched = true;
    seasonBtns.forEach(btn => {
        if (!btn.classList.contains('season-watched')) {
            allSeasonsWatched = false;
        }
    });
    
    const showWatchedBtn = document.querySelector(`.watch-btn.movie-watch-btn[data-show-id="${showId}"]`);
    if (showWatchedBtn) {
        if (allSeasonsWatched && seasonBtns.length > 0) {
            showWatchedBtn.classList.add('watched');
            showWatchedBtn.textContent = 'Watched ✓';
        } else {
            const anyEpisodeWatched = document.querySelectorAll(`.episode-watch-btn[data-show-id="${showId}"].watched`).length > 0;
            if (!anyEpisodeWatched) {
                showWatchedBtn.classList.remove('watched');
                showWatchedBtn.textContent = 'Mark as Watched';
            }
        }
    }
}