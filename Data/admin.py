from django.contrib import admin
from .models import News,StockPrice

admin.site.register(StockPrice)
admin.site.register(News)

