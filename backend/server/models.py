from django.db import models

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=40)
    github_access_token = models.CharField(max_length=40)
    dao_address = models.CharField(max_length=40)
