// ==============================
// HOME PAGE JAVASCRIPT
// ==============================

document.addEventListener('DOMContentLoaded', function() {
    // Set progress bar widths
    document.querySelectorAll('.progress-fill').forEach(function(el) {
        var progress = el.getAttribute('data-progress');
        if (progress !== null && progress !== '') {
            el.style.width = progress + '%';
        }
    });
});

// Scroll to episode on page load
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.hash) {
        const targetId = window.location.hash.substring(1);
        
        if (targetId.startsWith('season-')) {
            const episodeElement = document.getElementById(targetId);
            
            if (episodeElement) {
                let parent = episodeElement.parentElement;
                let seasonContainer = null;
                
                while (parent) {
                    if (parent.id && parent.id.startsWith('season')) {
                        seasonContainer = parent;
                        break;
                    }
                    parent = parent.parentElement;
                }
                
                if (seasonContainer) {
                    seasonContainer.classList.remove('d-none');
                    
                    const seasonHeader = seasonContainer.previousElementSibling;
                    if (seasonHeader && seasonHeader.classList.contains('season-header')) {
                        const arrow = seasonHeader.querySelector('.arrow');
                        if (arrow) {
                            arrow.classList.add('rotated');
                        }
                    }
                    
                    setTimeout(function() {
                        episodeElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        episodeElement.style.transition = '0.5s';
                        episodeElement.style.borderColor = 'var(--primary)';
                        episodeElement.style.boxShadow = '0 0 20px rgba(96, 165, 250, 0.3)';
                        setTimeout(function() {
                            episodeElement.style.borderColor = '';
                            episodeElement.style.boxShadow = '';
                        }, 3000);
                    }, 400);
                } else {
                    setTimeout(function() {
                        episodeElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 200);
                }
            }
        }
    }
});