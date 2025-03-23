# store/views.py

from django.shortcuts import render

def index(request):
    return render(request, 'store/base.html')