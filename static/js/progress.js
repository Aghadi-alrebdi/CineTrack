// ==============================
// SET PROGRESS BARS
// ==============================
document.addEventListener('DOMContentLoaded', function() {
    // Set progress bar widths
    document.querySelectorAll('.progress-bar').forEach(function(bar) {
        var progress = bar.getAttribute('data-progress');
        if (progress !== null && progress !== '') {
            bar.style.width = progress + '%';
            bar.setAttribute('aria-valuenow', progress);
        }
    });

    // Set progress-fill widths
    document.querySelectorAll('.progress-fill').forEach(function(el) {
        var progress = el.getAttribute('data-progress');
        if (progress !== null && progress !== '') {
            el.style.width = progress + '%';
        }
    });
});