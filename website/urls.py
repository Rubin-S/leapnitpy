from django.contrib import admin
from django.urls import path

from website import views

urlpatterns = [
    path('', views.home, name='home'),
    path('team', views.team, name='team'),
    path('study', views.study_page_route, name='study'),
    path('contact-us', views.contactus, name='contactus'),
    path('login', views.login_route, name='login'),
    path('signup', views.signup_route, name='signup'),
    path('logout', views.logout_route, name='logout'),
    path('profile', views.profile, name='profile'),
    path('test/<int:test_id>', views.route_test, name='test'),
    path('submit_test/<int:testId>/', views.submit_test, name='submit_test'),
    path('analyse/<int:test_id>/', views.analyse, name='analyse'),
    path('create_test/<int:chapter_id>/', views.create_test, name='create_test'),
]
