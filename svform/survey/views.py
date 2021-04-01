from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def introduce(request):
    return HttpResponse('introduceapp')


def vis_answer(request):
    return HttpResponse('answer your idea')


def result(request):
    return HttpResponse('endform')