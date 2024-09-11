from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Goal(models.Model):
    PRIORITY_CHOICES = [
        (1, 'High'),
        (2, 'Medium'),
        (3, 'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.PositiveIntegerField(choices=PRIORITY_CHOICES)  # Add choices here
    estimated_time = models.PositiveIntegerField(help_text='In minutes')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class Wish(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class TimeAllocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    google_calendar_event_id = models.CharField(max_length=255, null=True, blank=True)  # Add this field

    def __str__(self):
        return f"{self.goal.title} from {self.start_time} to {self.end_time}"

