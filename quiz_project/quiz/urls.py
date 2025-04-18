from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('quiz/<int:q_num>/', views.quiz, name='quiz'),
    path('result/', views.result, name='result'),
    path('register/', views.register, name='register'),  # Registration page
    path('login/', views.login_view, name='login'),     
]
