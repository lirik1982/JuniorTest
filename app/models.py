from django.db import models


class Deal(models.Model):
    customer = models.CharField(max_length=50)
    item = models.CharField(max_length=50)
    total = models.IntegerField()
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now=False, auto_now_add=False)
