from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Note(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=5000)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True)
