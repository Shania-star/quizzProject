from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres import fields
# Create your models here.
# Link to database


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # one to many relationship ( 1 user can create * categories)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank = True)

    def __str__(self):
        return self.name

class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question = models.CharField(max_length=250)
    answer = models.CharField(max_length=200)
    options = fields.ArrayField(models.CharField(max_length=200, blank=True))
    explanation = models.TextField(null = True, blank = True)
    number_wa = models.IntegerField(null = True, blank = True) 
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    point = models.FloatField(null = True, blank = True)

    def __str__(self):
        return self.question
    class Meta:
        ordering = ['-id']

class Number_Of_WrongA(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    number_wa = models.FloatField()

    def __str__(self):
        return str(self.question)

