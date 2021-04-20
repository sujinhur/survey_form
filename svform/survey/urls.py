from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('intro', views.introduce, name='intro'),
    path('problem', views.problem, name='problem'),
    path('result', views.result, name='result'),
]