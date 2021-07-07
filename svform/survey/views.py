from django.shortcuts import redirect, render
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from .models import StepCountData, QuestionCode, ResultData
import datetime
from dateutil.relativedelta import relativedelta
import random
import csv

# Create your views here.

# start page
def introduce(request):    
    return render(request, 'survey/intro.html')

# 예시 설명 페이지
def example(request):
    
    return render(request, 'survey/example.html')

# 주의사항 페이지
def attention(request):
    db_list = random_dblist()
    request.session['q_list'] = db_list
    request.session['id'] = request.session.session_key
    today = str(datetime.date.today().year) + "년 " + str(datetime.date.today().month) + "월 " + str(datetime.date.today().day) + "일"
    return render(request, 'survey/attention.html', context={'today':today})


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
        print(q_list)
        
        try:
            label, description, vis_date_1, vis_stepcount_1,vis_date_2, vis_stepcount_2, legend_value, y_value, data = maincode(page_index, q_list)
        except StepCountData.DoesNotExist:
            print("데이터를 불러오지 못했습니다. 새로고침을 해주시기 바랍니다.")
            label, description, vis_date_1, vis_stepcount_1,vis_date_2, vis_stepcount_2, legend_value, y_value, data = maincode(page_index, q_list)

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
            'y_value':y_value,
        }

        return render(request, 'survey/problem.html', context)

# 종료 페이지
def result(request):
    return render(request, 'survey/result.html')

# resultdata export csv
def exportcsv(request):
    resultdata = ResultData.objects.all()
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename=resultdata.csv'
    writer = csv.writer(response)
    writer.writerow(['ID', 'PID', 'Sequence', 'Pass/NoPass', 'Label', 'QueryData', 'Answer', 'QuestionDescription'])
    results = resultdata.values_list('id', 'pid', 'sequence', 'pnp', 'label', 'data', 'answer', 'q_dsc')
    for rlt in results:
        writer.writerow(rlt)
    return response

# 랜덤 db_list 생성하기
def random_dblist():
    today_db_list = random.sample(range(1,14), 10)
    specify_db_list = random.sample(range(16,20), 4) + random.sample(range(16,20),4)
    compare_db_list = random.sample(range(20,22),2) +random.sample(range(20,22),2) 
    db_index = today_db_list + specify_db_list + compare_db_list + [14, 15, 20, 22, 23, 23, 24, 25]
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
            vis_date.append(str(date[i].month) + '월 ' + str(date[i].day) + '일')    
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
                vis_date.append(str(date[i].year) + "년" + str(date[i].month) + "월")
                if len(vis_date) >= 2:
                    vis_stepcount.append(tmp_stepcount//date[i-1].day)
                    tmp_stepcount = 0
            if i == (len(date) -1):
                vis_stepcount.append(tmp_stepcount//date[i].day)
            
    return vis_date, vis_stepcount


# 비교 - 시각화 할 데이터만 정리
def compare_vis_data(date, stepcount, description):
    weekday = ['월', '화', '수', '목', '금', '토', '일']
    vis_date = []
    vis_stepcount = []
    
    if description == "주별 비교" or description == "이번주 저번주 비교":
        for i in range(len(date)):
            vis_date.append(weekday[i])
        vis_stepcount = stepcount

    elif description == "월별 비교" or description == "연도별 월별 비교" or description == "이번달 저번달 비교":
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
            y_value = "걸음 수"
        elif (end_date - start_date).days < 168:
            legend_value = "~ " + str(end_date.year) + "년 (주 평균)"
            y_value = "평균 걸음 수"
        else:
            legend_value = "~ " + str(end_date.year) + "년 (월)"
            y_value = "평균 걸음 수"
    elif label == "Specify":
        if (end_date - start_date).days < 32:
            legend_value = "~ " + str(end_date.year) + "년 " + str(end_date.month) + "월"
            y_value = "걸음 수"
        elif (end_date - start_date).days < 168:
            legend_value = "~ " + str(end_date.year) + "년 (주 평균)"
            y_value = "평균 걸음 수"
        else:
            legend_value = "~ " + str(end_date.year) + "년 (월)"
            y_value = "평균 걸음 수"
    else:
        if (end_date[0] - start_date[0]).days < 8:
            legend_value = [str(start_date[0]) + ' ~ ' + str(end_date[0]), str(start_date[1]) + ' ~ ' + str(end_date[1])]
            y_value = "걸음 수"
        elif (end_date[0] - start_date[0]).days > 35:
            legend_value = [str(start_date[0].year) + "년", str(start_date[1].year) + "년"]
            y_value = "걸음 수"
        else: 
            legend_value = [str(start_date[0].year) + "년 " + str(start_date[0].month) + '월', str(start_date[1].year) + "년 " + str(start_date[1].month) + '월']
            y_value = "평균 걸음 수"

    return legend_value, y_value

# 메인 코드
def maincode(page_index, q_list):
    # 날짜, 라벨 가져오기
    start_date, end_date, label, description = get_code(page_index, q_list)
    
    # 해당 기간 걸음수 받아오기
    date, stepcount = date_stepcount_data(start_date, end_date)

    # 범례값 
    legend_value, y_value = create_legend_value(start_date, end_date, label)

    # 시각화할 데이터 전처리
    vis_date_1 = []
    vis_date_2 = []
    vis_stepcount_1 = []
    vis_stepcount_2 = []
    data = []

    if label == 'Compare':
        vis_date_1, vis_stepcount_1 = compare_vis_data(date[0], stepcount[0], description)
        vis_date_2, vis_stepcount_2 = compare_vis_data(date[1], stepcount[1], description)
        vis_date_1, vis_stepcount_1 = str_date(vis_date_1, vis_stepcount_1)
        vis_date_2, vis_stepcount_2 = str_date(vis_date_2, vis_stepcount_2)
        data.append(createqurey(description, start_date[0], end_date[0]))
        data.append(createqurey(description, start_date[1], end_date[1]))
    else:
        vis_date_1, vis_stepcount_1 = today_vis_data(date, stepcount)
        vis_date_1, vis_stepcount_1 = str_date(vis_date_1, vis_stepcount_1)
        data.append(createqurey(description, start_date, end_date))
    print(data)
    print(vis_date_1, vis_stepcount_1)
    print(vis_date_2, vis_stepcount_2)

    return label, description, vis_date_1, vis_stepcount_1,vis_date_2, vis_stepcount_2, legend_value, y_value, data

# 쿼리 생성 함수  
def createqurey(description, start_date, end_date):
    day = (end_date - start_date).days 
    if description == '일일 걸음 수':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-" + str(day) + " days')  and date('now')"
    elif description == '주별 평균 걸음 수': 
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-" + str(day) + " days', 'weekday 1')  and date('now')"
    elif description == '월별 평균 걸음 수': 
        month = str((end_date.year - start_date.year) * 12 + end_date.month - start_date.month)
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-" + month + " month', 'start of month')  and date('now')"
    elif description == '최근 1주':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-6 days')  and date('now')"
    elif description == '최근 2주':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-13 days')  and date('now')"
    elif description == '최근 3주':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-20 days')  and date('now')"
    elif description == '최근 4주':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-27 days')  and date('now')"
    elif description == '이번달':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', 'start of month')  and date('now')"
    elif description == '최근 1달':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-1 month', '+1 days')  and date('now')"
    elif description == '최근 2달':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-2 month', '+1 days')  and date('now')"
    elif description == '최근 3달':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-3 month', '+1 days')  and date('now')"
    elif description == '최근 6달':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-6 month', '+1 days')  and date('now')"
    elif description == '최근 12달':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-12 month', '+1 days')  and date('now')"
    elif description == '저번주':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-7 days', 'weekday 1')  and date('now', '-7 days','weekday 0')"
    elif description == '저번달':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-1 month', 'start of month')  and date('now', 'start of month', '-1 days')"
    elif description == 'n월':
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN " + "'" + str(start_date) + "'" + " and date('" + str(start_date) + "', '+1 month', '-1 days')"
    elif description == 'n월 ~ m월':
        month = str((end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1)
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN " + "'" + str(start_date) + "'" + " and date('" + str(start_date) + "', '+" + month + " month', '-1 days')"
    elif description == 'n월 m째주': 
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN " + "'" + str(start_date) + "'" + " and date('" + str(start_date) + "', '+6 days')"
    elif description == "n월 m일부터 n'월 m'일까지":
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN '" + str(start_date) + "' and '" + str(end_date) + "'"
    elif description == "주별 비교":
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN '" + str(start_date) + "' and date('" + str(start_date) + "', '+6 days')"
    elif description == "월별 비교": 
        if end_date == datetime.date.today():
            return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN '" + str(start_date) + "' and date('now')"
        else:
            return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN '" + str(start_date) + "' and date('" + str(start_date) + "', '+1 month', '-1 days')"
    elif description == "연도별 비교": 
        if end_date == datetime.date.today():
            return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN '" + str(start_date) + "' and date('now')"
        else:
            return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN '" + str(start_date) + "' and date('" + str(start_date) + "', '+12 month', '-1 days')"
    else: 
        if end_date == datetime.date.today():
            return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN '" + str(start_date) + "' and date('now')"
        else:
            return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN '" + str(start_date) + "' and date('" + str(start_date) + "', '+1 month', '-1 days')"

