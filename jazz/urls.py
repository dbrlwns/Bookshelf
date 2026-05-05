from django.urls import path, include

from jazz.views import jazz_home, jazz_add

app_name = 'jazz'

urlpatterns = [
    path('', jazz_home, name='jazz'),
    path('/jazz_add', jazz_add, name='jazz_add'),
]