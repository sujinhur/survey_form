from django.shortcuts import redirect, render
from django.http.response import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import HttpResponse
from .models import StepCountData, QuestionCode, ResultData, PhoneNumber, Today, Specify, Compare
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

# 문제 예시 페이지
def problem_example(request):
    return render(request, 'survey/problem_example.html')

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
        resultdata.survey_date = request.session['survey_date']
    
        if request.session['label'] == 'Compare':
            resultdata.start_date_1 = request.session['start_date_1']
            resultdata.start_date_2 = request.session['start_date_2']
            resultdata.end_date_1 = request.session['end_date_1']
            resultdata.end_date_2 = request.session['end_date_2']
        else:
            resultdata.start_date_1 = request.session['start_date_1']
            resultdata.end_date_1 = request.session['end_date_1']

        resultdata.save()

        if request.session['sequence'] == 15:
            return redirect('event')
        else:
            return HttpResponseRedirect(reverse('problem', args=(page_index,)))

    else:
        next_page_index = page_index + 1

        # 세션에 저장된 db에 검색할 순서 
        q_list = {}
        q_list = request.session.get('q_list')
        
        try:
            label, description, vis_date_1, vis_stepcount_1,vis_date_2, vis_stepcount_2, legend_value, y_value, data, date_period, start_date, end_date = maincode(page_index, q_list)
        except StepCountData.DoesNotExist:
            label, description, vis_date_1, vis_stepcount_1,vis_date_2, vis_stepcount_2, legend_value, y_value, data, date_period, start_date, end_date = maincode(page_index, q_list)

        request.session['sequence'] = page_index
        request.session['label'] = label
        request.session['data'] = data
        request.session['description'] = description

        survey_date = datetime.date.today()
        request.session['survey_date'] = str(survey_date)
        if type(start_date) == list:
            request.session['start_date_1'] = str(start_date[0])
            request.session['start_date_2'] = str(start_date[1])
            request.session['end_date_1'] = str(end_date[0])
            request.session['end_date_2'] = str(end_date[1])
            
        else:
            request.session['start_date_1'] = str(start_date)
            request.session['end_date_1'] = str(end_date)


        context = {
            'page_index':page_index,
            'date_period': date_period,
            'next_page_index':next_page_index,
            'label': label,
            'date_1': vis_date_1,
            'stepcount_1':vis_stepcount_1,
            'date_2': vis_date_2,
            'stepcount_2':vis_stepcount_2,
            'legend_value':legend_value,
            'y_value':y_value,
            'description':description,
        }

        return render(request, 'survey/problem.html', context)

# enent 페이지
def event(request):
    if request.method == "POST":
        pid = ResultData.objects.latest('id')
        phoneNumber = PhoneNumber()
        phoneNumber.resultdata = pid
        phoneNumber.ph_num = request.POST.get('ph_num')
        phoneNumber.save()
        return redirect('result')
    return render(request, 'survey/insert_ph_num.html')

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

# phonenumber export csv
def exportcsv_phnum(request):
    phoneNumber = PhoneNumber.objects.all()
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename=phoneNumber.csv'
    writer = csv.writer(response)
    writer.writerow(['ID', 'resultdata', 'ph_num'])
    results = phoneNumber.values_list('id', 'resultdata', 'ph_num')
    for rlt in results:
        writer.writerow(rlt)
    return response

# 랜덤 db_list 생성하기
def random_dblist():
    today_db_list = random.sample([4, 5, 6, 7, 8, 10, 11, 12, 13], 5)
    specify_db_list = [14, 15, 16, 17, 19]
    compare_db_list = random.sample(range(20,26),5)  
    db_index = today_db_list + specify_db_list + compare_db_list 
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
        remainder = len(date) % 7
        cut = len(date) // 7
        tmp_stepcount = 0
        for i in range(len(date)):           
            tmp_stepcount = tmp_stepcount + stepcount[i]
            if (i+1) % 7 == 0:
                vis_date.append(str(date[i-6].month) + "월 " + str(date[i-6].day) + "일 ~ " + str(date[i].month) + "월 " + str(date[i].day) + "일")
                vis_stepcount.append(tmp_stepcount//7)
                tmp_stepcount = 0
            if remainder != 0 and i == cut * 7 + remainder -1:
                vis_date.append(str(date[i-remainder + 1].month) + "월 " + str(date[i-remainder + 1].day) + "일 ~ " + str(date[i].month) + "월 " + str(date[i].day) + "일")
                vis_stepcount.append(tmp_stepcount//remainder)

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
            y_value = "주별 평균 걸음 수"
        else:
            legend_value = "~ " + str(end_date.year) + "년 (월)"
            y_value = "월 평균 걸음 수"
    elif label == "Specify":
        if (end_date - start_date).days < 32:
            legend_value = "~ " + str(end_date.year) + "년 " + str(end_date.month) + "월"
            y_value = "걸음 수"
        elif (end_date - start_date).days < 168:
            legend_value = "~ " + str(end_date.year) + "년 (주 평균)"
            y_value = "주별 평균 걸음 수"
        else:
            legend_value = "~ " + str(end_date.year) + "년 (월)"
            y_value = "월 평균 걸음 수"
    else:
        if (end_date[0] - start_date[0]).days < 8:
            legend_value = [str(start_date[0]) + ' ~ ' + str(end_date[0]), str(start_date[1]) + ' ~ ' + str(end_date[1])]
            y_value = "걸음 수"
        elif (end_date[0] - start_date[0]).days > 35:
            legend_value = [str(start_date[0].year) + "년", str(start_date[1].year) + "년"]
            y_value = "걸음 수"
        else: 
            legend_value = [str(start_date[0].year) + "년 " + str(start_date[0].month) + '월', str(start_date[1].year) + "년 " + str(start_date[1].month) + '월']
            y_value = "월 평균 걸음 수"

    return legend_value, y_value

# 날짜 기간 가져오기
def date_section(start_date, end_date):
    if type(start_date) == list:
        date_period = str(start_date[0].year) + "년 " + str(start_date[0].month) + "월 " + str(start_date[0].day) + "일 ~ " + str(end_date[0].year) + "년 " + str(end_date[0].month) + "월 " + str(end_date[0].day) + "일, " + str(start_date[1].year) + "년 " + str(start_date[1].month) + "월 " + str(start_date[1].day) + "일 ~ " + str(end_date[1].year) + "년 " + str(end_date[1].month) + "월 " + str(end_date[1].day) + "일"
    else:
        date_period = str(start_date.year) + "년 " + str(start_date.month) + "월 " + str(start_date.day) + "일 ~ " + str(end_date.year) + "년 " + str(end_date.month) + "월 " + str(end_date.day) + "일"
    return date_period

# 메인 코드
def maincode(page_index, q_list):
    # 날짜, 라벨 가져오기
    start_date, end_date, label, description = get_code(page_index, q_list)
    
    # 해당 기간 걸음수 받아오기
    date, stepcount = date_stepcount_data(start_date, end_date)

    # 범례값 
    legend_value, y_value = create_legend_value(start_date, end_date, label)

    # 날짜 기간
    date_period = date_section(start_date, end_date)

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
        data.append(createqurey(description, start_date, end_date))
    else:
        vis_date_1, vis_stepcount_1 = today_vis_data(date, stepcount)
        vis_date_1, vis_stepcount_1 = str_date(vis_date_1, vis_stepcount_1)
        data.append(createqurey(description, start_date, end_date))

    return label, description, vis_date_1, vis_stepcount_1,vis_date_2, vis_stepcount_2, legend_value, y_value, data, date_period, start_date, end_date

# 쿼리 생성 함수  
def createqurey(description, start_date, end_date):
    if description == '일일 걸음 수':
        day = (end_date - start_date).days 
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-" + str(day) + " days')  and date('now')"
    elif description == '주별 평균 걸음 수': # 수정 필요
        day = (end_date - start_date).days 
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
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-14 days', 'weekday 1')  and date('now', '-7 days','weekday 0')"
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
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN '" + str(start_date[0]) + "' and date('" + str(start_date[0]) + "', '+6 days') or date BETWEEN '" + str(start_date[1]) + "' and date('" + str(start_date[1]) + "', '+6 days')"
    elif description == "월별 비교": 
        if end_date[0] == datetime.date.today():
            return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', 'start of month') and date('now') or date BETWEEN '" + str(start_date[1]) + "' and date('" + str(start_date[1]) + "', '+1 month', '-1 days')"
        else:
            return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN '" + str(start_date[0]) + "' and date('" + str(start_date[0]) + "', '+1 month', '-1 days') or date BETWEEN '" + str(start_date[1]) + "' and date('" + str(start_date[1]) + "', '+1 month', '-1 days')"
    elif description == "연도별 비교": 
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN '" + str(start_date[0]) + "' and date('now') or date BETWEEN '" + str(start_date[1]) + "' and date('" + str(start_date[1]) + "', '+12 month', '-1 days')"
    elif description == "연도별 월별 비교":
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN '" + str(start_date[0]) + "' and date('" + str(start_date[0]) + "', '+1 month', '-1 days') or date BETWEEN '" + str(start_date[1]) + "' and date('" + str(start_date[1]) + "', '+1 month', '-1 days')"
    elif description == "이번주 저번주 비교": 
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', '-7 days', 'weekday 1') and date('now') or date BETWEEN date('now', '-14 days', 'weekday 1') and date('now', '-7 days', 'weekday 0')"
    else: 
        return "SELECT * FROM survey_stepcountdata WHERE date BETWEEN date('now', 'start of month') and date('now') or date BETWEEN date('now', 'start of month', '-1 month') and date('now', 'start of month', '-1 days')"
        

# confirm page
@csrf_exempt
def confirm(request):
    if request.method == "POST":

        pnp = request.POST.get('inlineRadioOptions')
        
        resultpnp = ResultData.objects.get(id=request.session['idx'])
        resultpnp.pnp = pnp
        resultpnp.checked = 'checked'
        resultpnp.save()

        label = request.session['cf_label']
        answer = request.session['cf_answer']
        query = request.session['cf_query'] 

        if pnp == "True":
            if label == "Today":
                todaydata = Today()
                todaydata.resultdata = ResultData.objects.get(id=request.session['idx'])
                todaydata.answer = answer
                todaydata.query = query
                todaydata.save()

            elif label == "Specify":
                specifydata = Specify()
                specifydata.resultdata = ResultData.objects.get(id=request.session['idx'])
                specifydata.answer = answer
                specifydata.query = query
                specifydata.save()

            else:
                comparedata = Compare()
                comparedata.resultdata = ResultData.objects.get(id=request.session['idx'])
                comparedata.answer = answer
                comparedata.query = query
                comparedata.save()

        return redirect('confirm')
    

    else:
        try:
            idx = ResultData.objects.filter(checked__isnull = True)[0].id
        except IndexError:
            return HttpResponse('검수할 데이터가 없습니다.')

        request.session['idx'] = idx
        
        cf_data = ResultData.objects.get(id=idx)
        cf_query = cf_data.data
        cf_answer = cf_data.answer
        cf_label = cf_data.label
        cf_dsc = cf_data.q_dsc
        cf_survey_date = cf_data.survey_date


        start_date = []
        end_date = []
        if cf_label == 'Compare':
            start_date.append(cf_data.start_date_1)
            start_date.append(cf_data.start_date_2)
            end_date.append(cf_data.end_date_1)
            end_date.append(cf_data.end_date_2)
        else:
            start_date.append(cf_data.start_date_1)
            end_date.append(cf_data.end_date_1)

        request.session['cf_label'] = cf_label
        request.session['cf_answer'] = cf_answer
        request.session['cf_query'] = cf_query

        vis_date_1, vis_stepcount_1, vis_date_2, vis_stepcount_2, legend_value, y_value = confirm_vis_data(cf_label, cf_dsc, start_date, end_date)

        cf_query = cf_query[2:-2]

        context = {
            'cf_answer' : cf_answer,
            'cf_label' : cf_label,
            'cf_dsc' : cf_dsc,
            'cf_survey_date' : cf_survey_date,
            'cf_query' : cf_query.split('", "'),
            'legend_value' : legend_value,
            'y_value' : y_value,
            'date_1' : vis_date_1, 
            'stepcount_1' : vis_stepcount_1,
            'date_2' : vis_date_2, 
            'stepcount_2' : vis_stepcount_2,
        }
        return render(request, 'confirm/confirm.html', context)

# 검수 페이지 시각화 데이터 처리
def confirm_vis_data(cf_label, cf_dsc, start_date, end_date):
    vis_date_1 = []
    vis_stepcount_1 = []
    vis_date_2 = []
    vis_stepcount_2 = []
    
    if cf_label == 'Compare':
        date, stepcount = date_stepcount_data(start_date, end_date)
        vis_date_1, vis_stepcount_1 = compare_vis_data(date[0], stepcount[0], cf_dsc)
        vis_date_2, vis_stepcount_2 = compare_vis_data(date[1], stepcount[1], cf_dsc)
  
        vis_date_1, vis_stepcount_1 = str_date(vis_date_1, vis_stepcount_1)
        vis_date_2, vis_stepcount_2 = str_date(vis_date_2, vis_stepcount_2)

        legend_value, y_value = create_legend_value(start_date, end_date, cf_label)

    else:
        date, stepcount = date_stepcount_data(start_date[0], end_date[0])
        vis_date_1, vis_stepcount_1 = today_vis_data(date, stepcount)
        vis_date_1, vis_stepcount_1 = str_date(vis_date_1, vis_stepcount_1)
        legend_value, y_value = create_legend_value(start_date[0], end_date[0], cf_label)
    
    return vis_date_1, vis_stepcount_1, vis_date_2, vis_stepcount_2, legend_value, y_value


# todaydata export csv
def today_exportcsv(request):
    today_resultdata = Today.objects.all()
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename=today_resultdata.csv'
    writer = csv.writer(response)
    writer.writerow(['Resultdata', 'Answer', 'Query'])
    results = today_resultdata.values_list('resultdata', 'answer', 'query')
    for rlt in results:
        writer.writerow(rlt)
    return response

# specifydata export csv
def specify_exportcsv(request):
    specify_resultdata = Specify.objects.all()
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename=specify_resultdata.csv'
    writer = csv.writer(response)
    writer.writerow(['Resultdata', 'Answer', 'Query'])
    results = specify_resultdata.values_list('resultdata', 'answer', 'query')
    for rlt in results:
        writer.writerow(rlt)
    return response

# comparedata export csv
def compare_exportcsv(request):
    compare_resultdata = Compare.objects.all()
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename=compare_resultdata.csv'
    writer = csv.writer(response)
    writer.writerow(['Resultdata', 'Answer', 'Query'])
    results = compare_resultdata.values_list('resultdata', 'answer', 'query')
    for rlt in results:
        writer.writerow(rlt)
    return response