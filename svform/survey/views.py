from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse('hello')

def introduce(request):
    return render(request, 'survey/intro.html')


def problem(request):
    return render(request, 'survey/problem.html')


def result(request):
    return render(request, 'survey/result.html')