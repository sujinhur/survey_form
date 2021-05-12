from django.shortcuts import render
from django.http import HttpResponse
import datetime
from .models import StepCountData

# Create your views here.

def index(request):
    return HttpResponse('hello')

def introduce(request):
    return render(request, 'survey/intro.html')


def problem(request, page_index):
    start_date = datetime.date(2019,1,1)
    end_date = datetime.date(2019,1,7)

    next_page_index = page_index + 1
    date_list =  StepCountData.objects.raw("Select * from survey_stepcountdata where date BETWEEN date(%s) AND date(%s)", [start_date, end_date])
    print(date_list)
    context = {
        'date_list':date_list,
        'next_page_index':next_page_index
    }

    return render(request, 'survey/problem.html', context)


def result(request):
    return render(request, 'survey/result.html')