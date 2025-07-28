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

    path('dashboard/jobs/edit/<int:job_id>/', views.edit_job, name='edit_job'),
    path('dashboard/jobs/delete/<int:job_id>/', views.delete_job, name='delete_job'),

    path('dashboard/admit-cards/', views.manage_admit_cards, name='manage_admit_cards'),
    path('dashboard/admit-cards/edit/<int:card_id>/', views.edit_admit_card, name='edit_admit_card'),
    path('dashboard/admit-cards/delete/<int:card_id>/', views.delete_admit_card, name='delete_admit_card'),

    path('dashboard/results/', views.manage_results, name='manage_results'),
    path('dashboard/results/edit/<int:result_id>/', views.edit_result, name='edit_result'),
    path('dashboard/results/delete/<int:result_id>/', views.delete_result, name='delete_result'),


    path('dashboard/highlights/', views.manage_highlights, name='manage_highlights'),
    path('dashboard/highlights/edit/<int:highlight_id>/', views.edit_highlight, name='edit_highlight'),
    path('dashboard/highlights/delete/<int:highlight_id>/', views.delete_highlight, name='delete_highlight'),


    
]
