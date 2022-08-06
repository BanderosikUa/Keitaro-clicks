from django.urls import path, include
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='custom-login'),
    path('', MainView.as_view(), name='main')
]