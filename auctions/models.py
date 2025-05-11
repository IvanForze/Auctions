from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length = 60)

class Listing(models.Model):
    title = models.CharField(max_length = 60)
    description = models.CharField(max_length = 300)
    image = models.ImageField(upload_to='uploads/', default="test")
    price = models.FloatField()
    date = models.DateTimeField(default=datetime.now())
    owner = models.ForeignKey(User, on_delete = models.CASCADE, blank=True, null=True, related_name = "owner")
    category = models.ForeignKey(Category, on_delete = models.CASCADE, blank=True, null=True, related_name = "category")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name = "watchlist")

    def __str__(self):
        return f"{self.title}, {self.description}, {self.date}, {self.image}"


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete = models.CASCADE, blank=True, null=True, related_name = "listing")
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank=True, null=True, related_name = "user")
    text = models.CharField(max_length = 60)
    date = models.DateTimeField(default=datetime.now())
