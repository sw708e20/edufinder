from django.db import models


# Create your models here.
class Question(models.Model):
    question = models.CharField(max_length=200)


class Education(models.Model):
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=2000)


class EducationType(models.Model):
    education = models.ForeignKey(to=Education, on_delete=models.CASCADE)
    url = models.CharField(max_length=2000)
    name = models.CharField(max_length=120)
