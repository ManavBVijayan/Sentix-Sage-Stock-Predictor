from django.db import models


class ProcessLog(models.Model):
    date = models.DateField(auto_now_add=True)
    stock_status = models.BooleanField(default=False)
    bs_status = models.BooleanField(default=False)
    toi_status = models.BooleanField(default=False)
    model_training_status = models.BooleanField(default=False)
    mse = models.FloatField(null=True, blank=True)
    r2_score = models.FloatField(null=True, blank=True)
    day1 = models.FloatField(null=True, blank=True)
    day2 = models.FloatField(null=True, blank=True)
    day3 = models.FloatField(null=True, blank=True)
    day4 = models.FloatField(null=True, blank=True)
    day5 = models.FloatField(null=True, blank=True)
