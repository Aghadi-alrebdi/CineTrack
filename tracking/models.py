from django.db import models
from django.contrib.auth.models import User

class WatchHistory(models.Model):
    MEDIA_TYPES = [
        ('movie', 'Movie'),
        ('tv', 'TV Show'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    media_id = models.IntegerField()  # TMDB ID
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    title = models.CharField(max_length=200)
    poster_path = models.CharField(max_length=200, blank=True, null=True)
    watched = models.BooleanField(default=False)
    watchlist = models.BooleanField(default=False)
    rating = models.IntegerField(null=True, blank=True)  # 1-10
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'media_id', 'media_type']
        ordering = ['-date_updated']
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.media_type})"

class EpisodeWatchStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='episode_status')
    show_id = models.IntegerField()  # TMDB Show ID
    show_title = models.CharField(max_length=200)
    season_number = models.IntegerField()
    episode_number = models.IntegerField()
    episode_title = models.CharField(max_length=200, blank=True)
    watched = models.BooleanField(default=False)
    date_watched = models.DateTimeField(null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'show_id', 'season_number', 'episode_number']
        ordering = ['show_id', 'season_number', 'episode_number']
    
    def __str__(self):
        return f"{self.user.username} - S{self.season_number}E{self.episode_number} - {self.episode_title}"

class Comment(models.Model):
    MEDIA_TYPES = [
        ('movie', 'Movie'),
        ('tv', 'TV Show'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    media_id = models.IntegerField()  # TMDB ID
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    media_title = models.CharField(max_length=200)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.media_title} - {self.created_at.strftime('%Y-%m-%d')}"