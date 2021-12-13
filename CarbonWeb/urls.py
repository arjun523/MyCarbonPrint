from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('how_does_it_work',views.how_does_it_work,name='how_does_it_work'),
    path('home/error',views.error,name='error'),
    path('faqs',views.faqs,name='faqs'),
    path('home',views.index,name='index'),
    path('result',views.result,name='result'),
]
