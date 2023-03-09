from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    # path('about', views.about, name = 'about'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register', views.register, name = 'register'),

    path('<str:model_name>s', views.general_table_view, name = 'table-view'),
    path('<str:model_name>/add', views.model_add, name = "modelAdd"),
    
    path('participants/verify', views.participantsVerification, name = 'participantVerification'),

    path('test/<str:test_name>', views.participateInTest, name = "participate"),
]