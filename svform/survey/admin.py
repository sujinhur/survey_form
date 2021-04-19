from django.contrib import admin

from .models import ResultData, StepCountData, Today, Specify, Compare


# Register your models here.

admin.site.register(ResultData)

admin.site.register(Today)

admin.site.register(Specify)

admin.site.register(Compare)

admin.site.register(StepCountData)