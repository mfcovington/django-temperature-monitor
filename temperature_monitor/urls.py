from django.urls import path

from . import views


app_name = 'temperature_monitor'

urlpatterns = [
    path('', views.SensorList.as_view(), name='sensor_list'),
    path('<int:pk>/', views.SensorDetail.as_view(), name='sensor_detail'),
]
