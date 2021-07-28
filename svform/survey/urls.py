from django.urls import path

from django.conf.urls import url

from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.introduce, name='introduce'),
    path('example', views.example, name='example'),
    path('problem_example', views.problem_example, name='problem_example'),
    path('attention', views.attention, name='attention'),
    path('problem/<int:page_index>', views.problem, name='problem'),
    url(r'^problem/(?P<page_index>\w{0,50})', views.problem, name='problem'),
    path('event', views.event, name='event'), 
    path('result', views.result, name='result'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)