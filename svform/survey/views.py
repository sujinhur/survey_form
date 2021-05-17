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
    
    start_date, end_date, label = get_code(page_index, q_list)
    date, stepcount = date_stepcount_data(start_date, end_date)

    vis_date_1 = []
    vis_date_2 = []
    vis_stepcount_1 = []
    vis_stepcount_2 = []
    if type(start_date) == list:
        vis_date_1, vis_stepcount_1 = vis_data(date[0], stepcount[0])
        vis_date_2, vis_stepcount_2 = vis_data(date[1], stepcount[1])
        vis_date_1, vis_stepcount_1 = str_date(vis_date_1, vis_stepcount_1)
        vis_date_2, vis_stepcount_2 = str_date(vis_date_2, vis_stepcount_2)
    else:
        vis_date_1, vis_stepcount_1 = vis_data(date, stepcount)
        vis_date_1, vis_stepcount_1 = str_date(vis_date_1, vis_stepcount_1)


    context = {
        'date_1': vis_date_1,
        'stepcount_1':vis_stepcount_1,
        'date_2': vis_date_2,
        'stepcount_2':vis_stepcount_2,
        'label': label,
        'next_page_index':next_page_index,
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
    label = QuestionCode.objects.get(id=db_index[page_index - 1]).label
    loc = {}
    exec(code, globals(), loc)
    return loc["start_date"], loc["end_date"], label

# 날짜, 걸음수 데이터 받아오기
def date_stepcount_data(start_date, end_date):
    date = []
    stepcount = []
    if type(start_date) == list:
        
        for i in range(len(start_date)):
            tmp_date = []
            tmp_stepcount = []
            start_index = StepCountData.objects.get(date = start_date[i]).id
            end_index = StepCountData.objects.get(date = end_date[i]).id
            for j in range(start_index, end_index + 1):
                tmp_date.append(StepCountData.objects.get(id=j).date)
                tmp_stepcount.append(StepCountData.objects.get(id=j).stepcount)
            date.append(tmp_date)
            stepcount.append(tmp_stepcount)
            del tmp_date, tmp_stepcount

    else:
        start_index = StepCountData.objects.get(date = start_date).id
        end_index = StepCountData.objects.get(date = end_date).id
        for i in range(start_index, end_index + 1):
            date.append(StepCountData.objects.get(id=i).date)
            stepcount.append(StepCountData.objects.get(id=i).stepcount)
    return date, stepcount

# 시각화 할 데이터만 정리
def vis_data(date, stepcount):
    vis_date = []
    vis_stepcount = []

    
    if len(date) < 32:
        vis_date = date
        vis_stepcount = stepcount

    elif len(date) < 168:
        tmp_stepcount = 0
        for i in range(len(date)):           
            tmp_stepcount = tmp_stepcount + stepcount[i]
            if i % 7 == 0:
                vis_date.append(date[i])
                vis_stepcount.append(tmp_stepcount//7)
                tmp_stepcount = 0

    else:
        for i in range(len(date)):

            if date[i].month in vis_date == False:
                vis_date.append(date[i].month)
                vis_stepcount.append(tmp_stepcount//date[i].day)
                tmp_stepcount = 0
            else:
                tmp_stepcount = tmp_stepcount + stepcount[i]

    return vis_date, vis_stepcount

# 날짜 문자열로 변환
def str_date(date, stepcount):
    str_date_list = []
    str_stepcount_list = []
    for i in range(len(date)):
        str_date_list.append(str(date[i]))
        str_stepcount_list.append(str(stepcount[i]))
    return str_date_list, str_stepcount_list