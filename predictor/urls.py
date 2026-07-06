from django.urls import path

from . import views

app_name = 'predictor'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('predict/', views.predict_form, name='predict_form'),
    path('result/<int:pk>/', views.result_view, name='result'),
    path('history/<int:pk>/', views.history_detail, name='history_detail'),
]
