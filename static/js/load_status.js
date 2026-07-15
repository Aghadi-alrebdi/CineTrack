// ==============================
// LOAD USER STATUS on page load
// ==============================
document.addEventListener('DOMContentLoaded', function() {
    // Load watchlist status
    const watchlistBtns = document.querySelectorAll('.watchlist-btn');
    watchlistBtns.forEach(btn => {
        const mediaId = btn.dataset.mediaId;
        const mediaType = btn.dataset.mediaType;
        
        if (mediaId && mediaType) {
            fetch(`/tracking/api/get-user-status/?media_id=${mediaId}&media_type=${mediaType}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.watchlist) {
                        btn.classList.add('in-watchlist');
                        btn.textContent = 'In Watchlist';
                    }
                    
                    if (mediaType === 'movie') {
                        const watchedBtn = document.querySelector(`.watch-btn[data-media-id="${mediaId}"]`);
                        if (watchedBtn && data.watched) {
                            watchedBtn.classList.add('watched');
                            watchedBtn.textContent = 'Watched ✓';
                        }
                    }
                }
            })
            .catch(error => console.error('Error loading status:', error));
        }
    });

    // Load TV show watched status
    const tvWatchedBtns = document.querySelectorAll('.watch-btn.movie-watch-btn[data-show-id]');
    console.log('Found TV watched buttons:', tvWatchedBtns.length);
    
    tvWatchedBtns.forEach(btn => {
        const showId = btn.dataset.showId;
        console.log('Loading status for show ID:', showId);
        
        if (showId) {
            fetch(`/tracking/api/get-user-status/?media_id=${showId}&media_type=tv`)
            .then(response => response.json())
            .then(data => {
                console.log('TV show status response:', data);
                if (data.success && data.watched) {
                    btn.classList.add('watched');
                    btn.textContent = 'Watched ✓';
                    console.log('✅ Show marked as watched');
                } else {
                    btn.classList.remove('watched');
                    btn.textContent = 'Mark as Watched';
                    console.log('❌ Show is not watched');
                }
            })
            .catch(error => console.error('Error loading TV show status:', error));
        }
    });

    // Load EPISODE watch status
    const episodeBtns = document.querySelectorAll('.episode-watch-btn');
    episodeBtns.forEach(btn => {
        const showId = btn.dataset.showId;
        const seasonNumber = btn.dataset.seasonNumber;
        const episodeNumber = btn.dataset.episodeNumber;
        
        if (showId && seasonNumber && episodeNumber) {
            fetch(`/tracking/api/get-episode-status/?show_id=${showId}&season_number=${seasonNumber}&episode_number=${episodeNumber}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.watched) {
                    btn.classList.add('watched');
                    btn.textContent = 'Watched';
                }
            })
            .catch(error => console.error('Error loading episode status:', error));
        }
    });

    // Load SEASON watch status
    const seasonBtns = document.querySelectorAll('.season-watch-btn');
    seasonBtns.forEach(btn => {
        const showId = btn.dataset.showId;
        const seasonNumber = btn.dataset.seasonNumber;
        
        if (showId && seasonNumber) {
            fetch(`/tracking/api/get-season-status/?show_id=${showId}&season_number=${seasonNumber}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.watched) {
                        btn.classList.add('season-watched');
                        btn.textContent = 'Season Watched';
                    } else {
                        btn.classList.remove('season-watched');
                        btn.textContent = 'Mark Season';
                    }
                }
            })
            .catch(error => console.error('Error loading season status:', error));
        }
    });
});