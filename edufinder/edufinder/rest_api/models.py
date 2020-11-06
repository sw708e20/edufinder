from django.db import models


# Create your models here.
class Question(models.Model):
    en = models.CharField(max_length=200)
    da = models.CharField(max_length=200)


class Education(models.Model):
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=2000)


class EducationType(models.Model):
    education = models.ForeignKey(to=Education, related_name='education_types', on_delete=models.CASCADE)
    url = models.CharField(max_length=2000)
    name = models.CharField(max_length=120)


class AnswerChoice(models.TextChoices):
    YES = 'Yes'
    NO = 'No'
    PROBABLY = 'Probably'
    PROBABLY_NOT = "Probably not"
    DONT_KNOW = "Don't know"

class UserAnswer(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    ip_addr = models.GenericIPAddressField()
    education = models.ForeignKey(to=Education, on_delete=models.CASCADE)

class Answer(models.Model):
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)
    answer = models.CharField(choices=AnswerChoice.choices, max_length=20)
    userAnswer = models.ForeignKey(to=UserAnswer, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('question', 'userAnswer')

class AnswerConsensus(models.Model):
    education = models.ForeignKey(to=Education, on_delete=models.CASCADE)
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)
    answer = models.CharField(choices=AnswerChoice.choices, max_length=20)

    class Meta:
        unique_together = [['education', 'question']]