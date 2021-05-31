from django.urls import path

from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('intro', views.introduce, name='intro'),
    path('problem/<int:page_index>', views.problem, name='problem'),
    url(r'^problem/(?P<page_index>\w{0,50})', views.problem, name='problem'),
    path('result', views.result, name='result'),
]