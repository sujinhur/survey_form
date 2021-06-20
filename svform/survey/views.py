from django.shortcuts import redirect, render
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from .models import StepCountData, QuestionCode, ResultData
import datetime
from dateutil.relativedelta import relativedelta
import random

# Create your views here.

def index(request):
    return HttpResponse('hello')

# start page
def introduce(request):
    db_list = random_dblist()
    request.session['q_list'] = db_list
    request.session['id'] = request.session.session_key
    return render(request, 'survey/intro.html')

# 시각화 및 텍스트 입력 페이지
def problem(request, page_index):
    if request.method == "POST":
        if not request.session['id']:
            request.session['id'] = request.session.session_key

        resultdata = ResultData()
        resultdata.pid = request.session['id']
        resultdata.sequence = request.session['sequence']
        
        resultdata.label = request.session['label']
        resultdata.data = request.session['data']
        resultdata.answer = request.POST.get('answer')
        resultdata.q_dsc = request.session['description']
        resultdata.save()

        if request.session['sequence'] == 30:
            return redirect('result')
        else:
            return HttpResponseRedirect(reverse('problem', args=(page_index,)))

    else:
        next_page_index = page_index + 1

        # 세션에 저장된 db에 검색할 순서 
        q_list = {}
        q_list = request.session.get('q_list')
        
        label, description, vis_date_1, vis_stepcount_1,vis_date_2, vis_stepcount_2, legend_value, data = maincode(page_index, q_list)

        request.session['sequence'] = page_index
        request.session['label'] = label
        request.session['data'] = data
        request.session['description'] = description


        context = {
            'next_page_index':next_page_index,
            'label': label,
            'date_1': vis_date_1,
            'stepcount_1':vis_stepcount_1,
            'date_2': vis_date_2,
            'stepcount_2':vis_stepcount_2,
            'legend_value':legend_value,
        }

        try:
            return render(request, 'survey/problem.html', context)
        except StepCountData.DoesNotExist:
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
    description = QuestionCode.objects.get(id=db_index[page_index - 1]).description
    loc = {}
    exec(code, globals(), loc)
    return loc["start_date"], loc["end_date"], label, description

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

# 오늘 기준, 특정 기간 - 시각화 할 데이터만 정리
def today_vis_data(date, stepcount):
    vis_date = []
    vis_stepcount = []
    
    if len(date) < 32:
        for i in range(len(date)):
            vis_date.append(date[i].day)    
        vis_stepcount = stepcount

    elif len(date) < 168:
        tmp_stepcount = 0
        for i in range(len(date)):           
            tmp_stepcount = tmp_stepcount + stepcount[i]
            if (i+1) % 7 == 0:
                vis_date.append(str(date[i-6].month) + "월 " + str(date[i-6].day) + "일")
                vis_stepcount.append(tmp_stepcount//7)
                tmp_stepcount = 0

    else:
        tmp_stepcount = 0
        for i in range(len(date)):
            tmp_stepcount = tmp_stepcount + stepcount[i]
            if date[i].day == 1:
                vis_date.append(str(date[i].month) + "월")
                if len(vis_date) >= 2:
                    vis_stepcount.append(tmp_stepcount//date[i-1].day)
                    tmp_stepcount = 0
            if i == (len(date) -1):
                vis_stepcount.append(tmp_stepcount//date[i].day)
            
    return vis_date, vis_stepcount


# 비교 - 시각화 할 데이터만 정리
def compare_vis_data(date, stepcount):
    vis_date = []
    vis_stepcount = []
    
    if len(date) < 8:
        vis_date = ['월', '화', '수', '목', '금', '토', '일']
        vis_stepcount = stepcount

    elif len(date) < 32:
        for i in range(len(date)):
            vis_date.append(date[i].day)    
        vis_stepcount = stepcount

    else:
        tmp_stepcount = 0
        for i in range(len(date)):
            tmp_stepcount = tmp_stepcount + stepcount[i]
            if date[i].day == 1:
                vis_date.append(str(date[i].month) + "월")
                if len(vis_date) >= 2:
                    vis_stepcount.append(tmp_stepcount//date[i-1].day)
                    tmp_stepcount = 0
            if i == (len(date) -1):
                vis_stepcount.append(tmp_stepcount//date[i].day)

    return vis_date, vis_stepcount

# 날짜 문자열로 변환
def str_date(date, stepcount):
    str_date_list = []
    str_stepcount_list = []
    for i in range(len(date)):
        str_date_list.append(str(date[i]))
        str_stepcount_list.append(str(stepcount[i]))
    return str_date_list, str_stepcount_list

# 범례 구하기
def create_legend_value(start_date, end_date, label):
    if label == "Today":
        if (end_date - start_date).days < 32:
            legend_value = "~ " + str(end_date.month) + "월"
        else:
            legend_value = "~ " + str(end_date.year) + "년"
    elif label == "Specify":
        if (end_date - start_date).days < 32:
            legend_value = "~ " + str(end_date.year) + "년 " + str(end_date.month) + "월"
        else:
            legend_value = "~ " + str(end_date.year) + "년"
    else:
        if (end_date[0] - start_date[0]).days < 8:
            legend_value = [str(start_date[0]) + ' ~ ' + str(end_date[0]), str(start_date[1]) + ' ~ ' + str(end_date[1])]
        elif (end_date[0] - start_date[0]).days > 35:
            legend_value = [str(start_date[0].year) + "년", str(start_date[1].year) + "년"]
        else: 
            legend_value = [str(start_date[0].year) + "년 " + str(start_date[0].month) + '월', str(start_date[1].year) + "년 " + str(start_date[1].month) + '월']

    return legend_value

# 메인 코드
def maincode(page_index, q_list):
    # 날짜, 라벨 가져오기
    start_date, end_date, label, description = get_code(page_index, q_list)
    
    # 해당 기간 걸음수 받아오기
    date, stepcount = date_stepcount_data(start_date, end_date)

    # 범례값 
    legend_value = create_legend_value(start_date, end_date, label)

    # 시각화할 데이터 전처리
    vis_date_1 = []
    vis_date_2 = []
    vis_stepcount_1 = []
    vis_stepcount_2 = []
    data = []

    if label == 'Compare':
        vis_date_1, vis_stepcount_1 = compare_vis_data(date[0], stepcount[0])
        vis_date_2, vis_stepcount_2 = compare_vis_data(date[1], stepcount[1])
        vis_date_1, vis_stepcount_1 = str_date(vis_date_1, vis_stepcount_1)
        vis_date_2, vis_stepcount_2 = str_date(vis_date_2, vis_stepcount_2)
        data.append("SELECT * FROM survey_stepcountdata WHERE date BETWEEN " + "'" + str(start_date[0]) + "'" + " and " + "'" + str(end_date[0]) + "'")
        data.append("SELECT * FROM survey_stepcountdata WHERE date BETWEEN " + "'" + str(start_date[1]) + "'" + " and " + "'" + str(end_date[1]) + "'")
    else:
        vis_date_1, vis_stepcount_1 = today_vis_data(date, stepcount)
        vis_date_1, vis_stepcount_1 = str_date(vis_date_1, vis_stepcount_1)
        data.append("SELECT * FROM survey_stepcountdata WHERE date BETWEEN " + "'" + str(start_date) + "'" + " and " + "'" + str(end_date) + "'")

    print(data)
    print(vis_date_1, vis_stepcount_1)
    print(vis_date_2, vis_stepcount_2)

    return label, description, vis_date_1, vis_stepcount_1,vis_date_2, vis_stepcount_2, legend_value, data