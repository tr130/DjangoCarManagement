from django.db import models

# Create your models here.
class Part(models.Model):
    name = models.CharField(max_length=200)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    customer_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_level = models.PositiveIntegerField()

    def __str__(self):
        return self.name