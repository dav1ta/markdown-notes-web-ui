from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


# Create your models here.


class Tags(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user_subtabs = models.ManyToManyField(User, through='SubTags')
    def __str__(self):
        return self.name


class SubTags(models.Model):
    name = models.CharField(max_length=100, unique=True)
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # current user
    markdown = models.TextField()
    # current user
    def __str__(self):
        return self.name



class UserSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=100, default='light')
    edit_mode= models.BooleanField(default=True)
    def __str__(self):
        return self.user.username
