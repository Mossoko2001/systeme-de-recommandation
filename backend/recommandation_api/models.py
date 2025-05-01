from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Item(models.Model):
    TYPE_CHOICES = [
        ('book', 'Livre'),
        ('movie', 'Film'),
        ('article', 'Article'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    content_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    author = models.CharField(max_length=100, blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.content_type})"

class Interaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rating = models.IntegerField(null=True, blank=True)  # Ex : 1 à 5 étoiles
    clicked = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interaction - User: {self.user.username}, Item: {self.item.title}"
