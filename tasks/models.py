from django.db import models

# Create your models here.
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status_choices = (
        (1, 'To Do'),
        (2, 'In Progress'),
        (3, 'Completed'),
    )
    priority_choices = (
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    )
    status = models.IntegerField(choices=status_choices)
    priority = models.IntegerField(choices=priority_choices)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
