from django.db import models

class Feedback(models.Model):
    task_id = models.CharField(max_length=200)
    strategy = models.CharField(max_length=50, default='smart_balance')
    was_helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
