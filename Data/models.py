from django.db import models


class StockPrice(models.Model):
    date = models.DateField(primary_key=True)
    symbol = models.CharField(max_length=10)
    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()


class News(models.Model):
    date = models.DateField()
    headline = models.CharField(max_length=255)
    website = models.CharField(max_length=100)

    def __str__(self):
        return self.headline
