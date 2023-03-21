from django.db import models


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=17)

class Category(models.Model):
    name = models.CharField(max_length=75)

    def __str__(self):
        return self.name
class Transaction(models.Model):
    trans_date = models.DateTimeField("Data transakcji",auto_now=True)
    type = models.CharField(max_length=30)
    sum = models.DecimalField(decimal_places=2,max_length=20,max_digits=20)
    user = models.CharField(max_length=30)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
