from django.urls import path

from . import views


app_name = 'temperature_monitor'

urlpatterns = [
    path('', views.SensorList.as_view(), name='sensor_list'),
    path('<int:pk>/', views.SensorDetail.as_view(), name='sensor_detail'),
    path('gateways/', views.GatewayList.as_view(), name='gateway_list'),
    path('gateways/<int:pk>/', views.GatewayDetail.as_view(), name='gateway_detail'),
]
