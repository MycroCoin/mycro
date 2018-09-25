from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass


# Create your models here.
class Project(models.Model):
    repo_name = models.CharField(max_length=40)
    dao_address = models.CharField(max_length=42, unique=True)
    merge_module_address = models.CharField(max_length=42)
    last_merge_event_block = models.PositiveIntegerField(default=0)
    is_mycro_dao = models.BooleanField(default=False)
    symbol = models.CharField(max_length=10, default=None, blank=False,
                              null=True)
    decimals = models.IntegerField(default=-1)

    # TODO use django managers
    @staticmethod
    def get_mycro_dao():
        try:
            return Project.objects.get(is_mycro_dao=True)
        except:
            return None

    @staticmethod
    def create_mycro_dao(address, symbol, decimals):
        Project.objects.filter().update(is_mycro_dao=False)
        return Project.objects.create(
                repo_name='mycro',
                dao_address=address,
                is_mycro_dao=True,
                symbol=symbol,
                decimals=decimals)

    def __str__(self):
        return f'{self.repo_name}@{self.dao_address}'

    def __repr(self):
        return self.__str__()


class ASC(models.Model):
    address = models.CharField(max_length=42, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    rewardee = models.CharField(max_length=42)
    reward = models.IntegerField()
    pr_id = models.IntegerField(null=True, blank=True)
