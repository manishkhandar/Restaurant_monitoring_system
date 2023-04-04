from django.urls import path
from api.controller.views import *

urlpatterns = [
    path('trigger_report/', trigger_report),
    path('get_report/', get_report)
]
