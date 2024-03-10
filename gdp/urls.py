from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('line/', views.line, name='linechart'),
    path('csv/', views.gdp_csv, name='csv'),
]
