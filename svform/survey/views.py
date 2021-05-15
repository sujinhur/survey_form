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
    db_list = random_dblist()
    request.session['q_list'] = db_list
    return render(request, 'survey/intro.html')

# 시각화 및 텍스트 입력 페이지
def problem(request, page_index):
    next_page_index = page_index + 1


    q_list = {}
    q_list = request.session.get('q_list')
    
    start_date, end_date = get_code(page_index, q_list)

    date_list = []
    if type(start_date) == list:
        for i in range(len(start_date)):
            date_list.append(StepCountData.objects.raw("Select * from survey_stepcountdata where date BETWEEN date(%s) AND date(%s)", [start_date[i], end_date[i]]))
    else:
        date_list.append(StepCountData.objects.raw("Select * from survey_stepcountdata where date BETWEEN date(%s) AND date(%s)", [start_date, end_date]))
    
    context = {
        'date_list':date_list,
        'next_page_index':next_page_index
    }

    return render(request, 'survey/problem.html', context)

# 종료 페이지
def result(request):
    return render(request, 'survey/result.html')

# 랜덤 db_list 생성하기
def random_dblist():
    today_db_list = random.sample(range(1,14), 10)
    specify_db_list = random.sample(range(16,20), 4) + random.sample(range(16,20),4)
    compare_db_list = random.sample(range(20,24),4) +random.sample(range(20,24),4) +random.sample(range(20,24),2)
    db_index = today_db_list + specify_db_list + compare_db_list + [14, 15]
    random.shuffle(db_index)
    return db_index

# 날짜 기간 랜덤 코드
def get_code(page_index, db_index): 
    code = QuestionCode.objects.get(id=db_index[page_index - 1]).code
    loc = {}
    exec(code, globals(), loc)
    return loc["start_date"], loc["end_date"]