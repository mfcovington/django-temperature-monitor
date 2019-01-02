from django.urls import path

from . import views


app_name = 'temperature_monitor'

urlpatterns = [
    path('', views.home, name='home'),
    path('gateways/', views.GatewayList.as_view(), name='gateway_list'),
    path('gateways/<int:pk>/', views.GatewayDetail.as_view(), name='gateway_detail'),
    path('queries/', views.QueryList.as_view(), name='query_list'),
    path('sensors/', views.SensorList.as_view(), name='sensor_list'),
    path('sensors/<int:pk>/', views.SensorDetail.as_view(), name='sensor_detail'),
]
