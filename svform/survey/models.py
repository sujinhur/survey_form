from django.db import models
from django.db.models.base import Model

# Create your models here.

# all dataset(설문 결과 및 생성된 쿼리)
# pid - user ip address, sequence - answer count, pnp - usable or not, 
# label - labeling, data - query, answer - user answer
class ResultData(models.Model):
    pid = models.IntegerField() 
    sequence = models.IntegerField(default=0)
    pnp = models.BooleanField()
    Label_Choices = [
        ('Today', 'Today'),
        ('Specify', 'Specify'),
        ('Compare', 'Compare'),
    ]
    label = models.CharField(max_length=8, choices=Label_Choices)
    data = models.CharField(max_length=100)
    answer = models.TextField()


# Today dataset(resultdata에서 label이 Today이고 pnp가 True인 data)
# answer - user answer, date1 - start date
class Today(models.Model):
    resultdata = models.ForeignKey('ResultData', on_delete= models.CASCADE, db_column='resultdata_id')
    answer = models.TextField()
    date1 = models.CharField(max_length=15)


# Today dataset(resultdata에서 label이 Specify이고 pnp가 True인 data)
# answer - user answer, date1 - start date, date2 - end date
class Specify(models.Model):
    resultdata = models.ForeignKey('ResultData', on_delete= models.CASCADE, db_column='resultdata_id')
    answer = models.TextField()
    date1 = models.CharField(max_length=15)
    date2 = models.CharField(max_length=15)


# Today dataset(resultdata에서 label이 Compare이고 pnp가 True인 data)
# answer - user answer, date1 - start date, date2 - end date, date3 - next start date, date4 - next end date
class Compare(models.Model):
    resultdata = models.ForeignKey('ResultData', on_delete= models.CASCADE, db_column='resultdata_id')
    answer = models.TextField()
    date1 = models.CharField(max_length=15)
    date2 = models.CharField(max_length=15)
    date3 = models.CharField(max_length=15)
    date4 = models.CharField(max_length=15)

# 걸음 수 데이터 
class StepCountData(models.Model):
    date = models.DateField()
    stepcount = models.IntegerField()

    def __str__(self):
        return self.date

# 질문 코드
class QuestionCode(models.Model):
    label = models.CharField(max_length=10)
    code = models.TextField()
    description = models.CharField(max_length=30)