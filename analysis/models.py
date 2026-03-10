from django.db import models
from django.contrib.auth.models import User

class AudioFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audio_files', null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='audio/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Audio {self.id}"

class AnalysisResult(models.Model):
    audio_file = models.OneToOneField(AudioFile, on_delete=models.CASCADE, related_name='analysis')
    transcription = models.TextField(blank=True)
    wpm = models.FloatField(default=0.0)
    total_fillers = models.IntegerField(default=0)
    filler_details = models.JSONField(default=dict)  # Store filler word counts
    pause_count = models.IntegerField(default=0)
    total_pause_duration = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)
    ai_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.audio_file}"
