from django.urls import path
from. import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admit_cards/', views.admit_cards, name='admit_cards'),
    path('results/', views.results, name='results'),
    path('syllabus/', views.syllabus, name='syllabus'),
    path('contact/', views.contact, name='contact'),

    path('dashboard/login/', views.dashboard_login, name='dashboard_login'),
    path('dashboard/logout/', views.dashboard_logout, name='dashboard_logout'),
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/jobs/', views.manage_jobs, name='manage_jobs'),
    
]
