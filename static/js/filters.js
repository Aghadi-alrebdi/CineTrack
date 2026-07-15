// ==============================
// FILTER BUTTONS (Genre filters for trending/popular pages)
// ==============================
document.addEventListener('DOMContentLoaded', function() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const urlParams = new URLSearchParams(window.location.search);
    const currentGenre = urlParams.get('genre');
    
    filterBtns.forEach(function(btn) {
        const isAll = btn.textContent.trim() === 'All';
        const onclickAttr = btn.getAttribute('onclick');
        let genreId = null;
        if (onclickAttr) {
            const match = onclickAttr.match(/genre=(\d+)/);
            if (match) {
                genreId = match[1];
            }
        }
        
        if (isAll && !currentGenre) {
            btn.style.background = 'var(--primary)';
            btn.style.color = 'var(--bg-primary)';
            btn.style.border = 'none';
            btn.style.fontWeight = '600';
        } else if (genreId && currentGenre === genreId) {
            btn.style.background = 'var(--primary)';
            btn.style.color = 'var(--bg-primary)';
            btn.style.border = 'none';
            btn.style.fontWeight = '600';
        } else {
            btn.style.background = 'transparent';
            btn.style.color = 'var(--text-secondary)';
            btn.style.border = '1px solid var(--border-color)';
            btn.style.fontWeight = '500';
        }
    });
});