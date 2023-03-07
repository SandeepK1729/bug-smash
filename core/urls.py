from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    # path('about', views.about, name = 'about'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register', views.register, name = 'register'),
    
    path('participants', views.view_participants, name = 'participants'),
    path('participants/verify', views.participantsVerification, name = 'participantVerification'),

    path('questions/add', views.upload_question, name = 'add question'),
    path('questions', views.view_questions, name = 'questions'),
    
]