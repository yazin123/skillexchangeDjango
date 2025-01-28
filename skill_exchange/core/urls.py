# core/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
   path('logout/', views.logout_view, name='logout'), 
    path('dashboard/', views.dashboard, name='dashboard'),
    path('skills/', views.skill_list, name='skill_list'),
    path('skills/add/', views.add_skill, name='add_skill'),
    path('skills/delete/<int:skill_id>/', views.delete_user_skill, name='delete_user_skill'),

]
urlpatterns += [
    path('find-matches/', views.find_matches, name='find_matches'),
    path('request-session/<int:teacher_id>/<int:skill_id>/', views.request_session, name='request_session'),
    path('my-sessions/', views.session_list, name='session_list'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('session/<int:session_id>/update-status/', views.update_session_status, name='update_session_status'),
]

urlpatterns += [
    path('session/<int:session_id>/review/', views.add_review, name='add_review'),
    path('reviews/teacher/<int:teacher_id>/', views.teacher_reviews, name='teacher_reviews'),
]

urlpatterns += [
    path('messages/', views.message_list, name='message_list'),
    path('messages/sent/', views.sent_messages, name='sent_messages'),
    path('messages/compose/<int:receiver_id>/', views.compose_message, name='compose_message'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('messages/delete/<int:message_id>/', views.delete_message, name='delete_message'),
]