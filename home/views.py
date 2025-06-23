from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return HttpResponse('<h1>Welcome to PopWorld!</h1><p>This is the home page.</p>')
