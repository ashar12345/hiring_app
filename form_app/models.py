from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Document(models.Model):
    email = models.EmailField(primary_key = True,max_length=255)
    document = models.FileField(upload_to='docs', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    domain = models.CharField(max_length=255)
    exp_years = models.IntegerField()
    salary = models.IntegerField()
    exp_salary = models.IntegerField()
    skillset = models.CharField(max_length=255)
