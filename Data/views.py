from django.shortcuts import render
from Data.models import StockPrice
from AdminDashBoard.models import ProcessLog
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64


def home(request):
    return render(request, 'home.html')


# views.py

def explore(request):
    # Fetch last 30 days' stock close prices
    last_30_days_data = StockPrice.objects.order_by('-date')[:30]
    dates = [data.date.strftime('%Y-%m-%d') for data in last_30_days_data]  # Convert date objects to strings
    close_prices = [data.close_price for data in last_30_days_data]

    # Fetch predictions for the next five days
    last_process_log = ProcessLog.objects.last()
    predictions = [last_process_log.day1, last_process_log.day2, last_process_log.day3, last_process_log.day4, last_process_log.day5]

    # Calculate dates for the next five days
    last_date = last_30_days_data[0].date
    prediction_dates = [(last_date + datetime.timedelta(days=i + 1)).strftime('%Y-%m-%d') for i in range(5)]

    # Combine close prices and predictions into a single list of tuples
    combined_data = list(zip(dates, close_prices)) + list(zip(prediction_dates, predictions))

    # Sort the combined data by date
    sorted_data = sorted(combined_data, key=lambda x: x[0])

    # Extract sorted dates and values
    sorted_dates = [data[0] for data in sorted_data]
    sorted_values = [data[1] for data in sorted_data]

    context = {
        'dates': sorted_dates,
        'values': sorted_values,
    }

    return render(request, 'explore.html', context)
