from typing import Text
from django.db import models
from django.conf import settings
from django.db.models.fields import AutoField
from django.utils import timezone
# Create your models here.

class Product(models.Model):
    id =models.IntegerField(primary_key=True)
    title=models.CharField(max_length=255)
    price= models.FloatField()
    description= models.TextField()
    category=models.TextField()
    image=models.URLField()

    def __str__(self) -> str:
        return self.title