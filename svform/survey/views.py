from django.shortcuts import render
from django.http import HttpResponse
import datetime
from .models import StepCountData, QuestionCode
from dateutil.relativedelta import relativedelta
import random

# Create your views here.

def index(request):
    return HttpResponse('hello')

# start page
def introduce(request):
    return render(request, 'survey/intro.html')

# 시각화 및 텍스트 입력 페이지
def problem(request, page_index):
    next_page_index = page_index + 1

    start_date, end_date = get_code(page_index)
    date_list =  StepCountData.objects.raw("Select * from survey_stepcountdata where date BETWEEN date(%s) AND date(%s)", [start_date, end_date])

    context = {
        'date_list':date_list,
        'next_page_index':next_page_index
    }

    return render(request, 'survey/problem.html', context)

# 종료 페이지
def result(request):
    return render(request, 'survey/result.html')

# 날짜 기간 랜덤 코드
def get_code(page_index): 
    code = QuestionCode.objects.get(id=1).code
    loc = {}
    exec(code, globals(), loc)
    return loc["start_date"], loc["end_date"]