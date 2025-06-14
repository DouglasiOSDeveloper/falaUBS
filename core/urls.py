from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('vaccination/', views.vaccination_view, name='vaccination'),
    path('scheduling/', views.scheduling_view, name='scheduling'),
    path('ubs-nearby/', views.ubs_nearby_view, name='ubs_nearby'),
    path('ubs-detail/<str:ubs_name>/', views.ubs_detail_view, name='ubs_detail'),
]
