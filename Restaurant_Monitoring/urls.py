
from django.contrib import admin
from django.urls import path, include
from api.controller import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('uploadcsv/', views.uploadcsv),
    path("api/", include('api.routes.urls'))
]
