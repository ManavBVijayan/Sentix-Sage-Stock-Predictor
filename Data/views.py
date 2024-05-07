from django.shortcuts import render
from django.http import HttpResponse
from .news_data import bs_news_setup, toi_news_setup, remove_duplicates, save_new_data


def home(request):
    return render(request, 'home.html')
