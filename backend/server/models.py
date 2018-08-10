from django.db import models

# Create your models here.
class Project(models.Model):
    repo_name = models.CharField(max_length=40)
    dao_address = models.CharField(max_length=42, unique=True)
    merge_module_address = models.CharField(max_length=42)
    last_merge_event_block = models.PositiveIntegerField(default=0)
    is_mycro_dao = models.BooleanField(default=False)

    # TODO use django managers
    @staticmethod
    def get_mycro_dao():
        try:
            return Project.objects.get(is_mycro_dao=True)
        except:
            return None

    @staticmethod
    def create_mycro_dao(address):
        Project.objects.filter().update(is_mycro_dao=False)
        return Project.objects.create(dao_address=address, is_mycro_dao=True)


    def __str__(self):
        return f'{self.repo_name}@{self.dao_address}'

    def __repr(self):
        return self.__str__()


class ASC(models.Model):
    address = models.CharField(max_length=42, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    rewardee = models.CharField(max_length=42)

