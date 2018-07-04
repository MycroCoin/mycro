from django.db import models

# Create your models here.
class Project(models.Model):
    repo_name = models.CharField(max_length=40)
    dao_address = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return f'{self.repo_name}@{self.dao_address}'

    def __repr(self):
        return self.__str__()


class ASC(models.Model):
    address = models.CharField(max_length=40, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

