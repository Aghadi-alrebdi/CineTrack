// ==============================
// RATING STARS
// ==============================
document.addEventListener('DOMContentLoaded', function() {
    // Load existing ratings
    document.querySelectorAll('.rating-container').forEach(function(container) {
        const mediaId = container.dataset.mediaId;
        const mediaType = container.dataset.mediaType;
        
        if (mediaId && mediaType) {
            fetch(`/tracking/api/get-rating/?media_id=${mediaId}&media_type=${mediaType}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.rating) {
                    updateStars(container, data.rating);
                }
            })
            .catch(error => console.error('Error loading rating:', error));
        }
    });

    // Star hover and click events
    document.querySelectorAll('.rating-stars').forEach(function(starsContainer) {
        const container = starsContainer.closest('.rating-container');
        if (!container) return;
        
        const mediaId = container.dataset.mediaId;
        const mediaType = container.dataset.mediaType;
        
        starsContainer.querySelectorAll('.star').forEach(function(star) {
            star.addEventListener('mouseenter', function() {
                const value = parseInt(this.dataset.value);
                highlightStars(starsContainer, value);
                updateRatingText(container, value);
            });
            
            star.addEventListener('mouseleave', function() {
                const currentRating = parseInt(container.dataset.currentRating) || 0;
                highlightStars(starsContainer, currentRating);
                updateRatingText(container, currentRating);
            });
            
            star.addEventListener('click', function() {
                const value = parseInt(this.dataset.value);
                saveRating(container, mediaId, mediaType, value);
            });
        });
    });
});

function highlightStars(container, count) {
    container.querySelectorAll('.star').forEach(function(star) {
        const value = parseInt(star.dataset.value);
        if (value <= count) {
            star.classList.add('active');
            star.style.color = '#FBBF24';
        } else {
            star.classList.remove('active');
            star.style.color = 'var(--text-muted)';
        }
    });
}

function updateRatingText(container, rating) {
    const textElement = container.querySelector('.rating-text');
    const emojiElement = container.querySelector('.rating-emoji');
    
    if (textElement) {
        textElement.textContent = rating + '/10';
    }
    
    if (emojiElement) {
        const emojis = ['😢', '😕', '😐', '🙂', '😊', '😄', '🔥', '🌟', '⭐', '🎯'];
        const index = Math.min(Math.max(rating - 1, 0), 9);
        emojiElement.textContent = rating > 0 ? emojis[index] : '⭐';
    }
}

function updateStars(container, rating) {
    const starsContainer = container.querySelector('.rating-stars');
    container.dataset.currentRating = rating;
    highlightStars(starsContainer, rating);
    updateRatingText(container, rating);
}

function saveRating(container, mediaId, mediaType, rating) {
    const starsContainer = container.querySelector('.rating-stars');
    starsContainer.style.opacity = '0.5';
    
    const title = container.dataset.title || '';
    const posterPath = container.dataset.poster || '';
    
    fetch('/tracking/api/rate-media/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            media_id: parseInt(mediaId),
            media_type: mediaType,
            rating: rating,
            title: title,
            poster_path: posterPath,
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            container.dataset.currentRating = rating;
            highlightStars(starsContainer, rating);
            updateRatingText(container, rating);
            console.log(' Rating saved:', rating);
        } else {
            console.error('Error saving rating:', data.error);
            const currentRating = parseInt(container.dataset.currentRating) || 0;
            highlightStars(starsContainer, currentRating);
            updateRatingText(container, currentRating);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const currentRating = parseInt(container.dataset.currentRating) || 0;
        highlightStars(starsContainer, currentRating);
        updateRatingText(container, currentRating);
    })
    .finally(() => {
        starsContainer.style.opacity = '1';
    });
}