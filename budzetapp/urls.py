from django.urls import path
from django.contrib import admin
from . import views
from django.conf.urls import *
from .views import wykreskolowy
urlpatterns = [
    path('home', views.home, name='home'),
    path('userInterface', views.userInterface, name='userInterface'),
    path('przychody', views.przychody, name='przychody'),
    path('wydatki', views.wydatki, name='wydatki'),
    path('wykresy_filtrowanie', views.wykresy_filtrowanie, name='wykresy_filtrowanie'),
    path('transakcje', views.transakcje, name='transakcje'),
    path('wykresslupkowy', views.wykresslupkowy.as_view(), name='wykresslupkowy'),
    path('wykresslupkowywykres', views.wykresslupkowywykres, name='wykresslupkowywykres'),
    path('wykreskolowy', views.wykreskolowy.as_view(), name='wykreskolowy'),
    path('transakcjefiltrowanie', views.transakcjefiltrowanie, name='transakcjefiltrowanie'),
    path('rejestracja',views.rejestracja,name='rejestracja'),
    path('transakcjefiltrowaniedatapomiedzy', views.transakcjefiltrowaniedatapomiedzy, name='transakcjefiltrowaniedatapomiedzy'),
    path('pdf', views.pdf, name='pdf'),
]