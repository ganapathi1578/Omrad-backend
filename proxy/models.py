from django.db import models
from django.conf import settings

class UsageLog(models.Model):
    # Links this log to the exact Customer who made the request
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='api_logs'
    )
    
    # Metadata tracking
    prompt_tokens = models.IntegerField()
    completion_tokens = models.IntegerField()
    total_tokens = models.IntegerField()
    model_used = models.CharField(max_length=100, default="gemini-2.5-flash")
    
    # Automatically saves the exact time of the request
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.total_tokens} tokens"