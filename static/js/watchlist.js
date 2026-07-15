// ==============================
// WATCHLIST BUTTON TOGGLE
// ==============================
function toggleWatchlist(button) {
    const mediaId = button.dataset.mediaId;
    const mediaType = button.dataset.mediaType;
    const title = button.dataset.title;
    const posterPath = button.dataset.posterPath;
    
    if (!mediaId || !mediaType) {
        console.error('Missing media data');
        return;
    }
    
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    button.disabled = true;
    
    fetch('/tracking/api/toggle-watchlist/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            media_id: mediaId,
            media_type: mediaType,
            title: title,
            poster_path: posterPath,
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.in_watchlist) {
                button.classList.add('in-watchlist');
                button.textContent = 'In Watchlist';
            } else {
                button.classList.remove('in-watchlist');
                button.textContent = 'Add to Watchlist';
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