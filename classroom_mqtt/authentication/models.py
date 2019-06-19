from django.contrib.auth.models import User
from django.db import models


class Usertype(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Topic(models.Model):
    topic = models.CharField(max_length=100)

    def __str__(self):
        return self.topic


class Messages(models.Model):
    topic = models.CharField(max_length=100)
    message = models.CharField(max_length=100)

    def __str__(self):
        return self.topic


class SentFiles(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SentKey(models.Model):
    key = models.CharField(max_length=100)

    def __str__(self):
        return self.key
