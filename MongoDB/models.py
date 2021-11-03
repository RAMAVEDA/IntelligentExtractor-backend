# from django.db import models
from djongo import models
# from django_mongodb_engine.storage import GridFSStorage
# from djongo.storage import Gr
# Create your models here.


class ExtractFIle(models.Model):
    def directory(self, instance):
        print(
            'Extract/{0}_folder/{1}'.format(self.filename[:-4], self.filename))
        return 'Extract/{0}_folder/{1}'.format(self.filename[:-4], self.filename)
    filename = models.CharField(max_length=100)
    file = models.FileField(upload_to=directory, null=True, blank=True)
    modelname = models.CharField(max_length=200, blank=True)
    fieldextract = models.TextField(blank=True)
    coordinates = models.TextField(blank=True)
    eachfile = models.TextField(blank=True)
    originalname = models.CharField(max_length=200, blank=True)

    def __str__(self) -> str:
        return str(self.fieldextract)


class File(models.Model):
    # def directory(self, instance):
    #     print(
    #         'Upload/{0}_folder/{1}'.format(self.filename[:-4], self.filename))
    #     return 'Upload/{0}_folder/{1}'.format(self.filename[:-4], self.filename)
    filename = models.CharField(max_length=100)
    # file = models.FileField(upload_to=directory, null=True, blank=True)
    eachfile = models.TextField(blank=True)
    modelname = models.CharField(max_length=200, blank=True)
    filedetail = models.TextField(blank=True)
    id = models.ObjectIdField()

    def __str__(self) -> str:
        return str(self.filename)


class Document(models.Model):
    modelname = models.CharField(max_length=100)
    modeltype = models.CharField(max_length=100)
    id = models.ObjectIdField()
    fieldcount = models.IntegerField(default=0)
    finished = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.modelname)


class Field(models.Model):
    fieldname = models.CharField(max_length=100)
    fieldtype = models.CharField(max_length=100)
    mandatory = models.BooleanField()
    id = models.ObjectIdField()
    fieldcoor = models.CharField(max_length=500, blank=True)
    modelname = models.CharField(max_length=100)

    def __str__(self) -> str:
        return str(self.fieldname)


class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100,blank=True)
    lastname = models.CharField(max_length=100,blank=True)
    email = models.CharField(max_length=100,blank=True)

    def __str__(self) -> str:
        return str(self.username)