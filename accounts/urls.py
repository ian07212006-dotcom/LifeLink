from django.urls import path

from .views import lookups, register


urlpatterns = [
    path('lookups/', lookups, name='api-lookups'),
    path('register/', register, name='api-register'),
]
