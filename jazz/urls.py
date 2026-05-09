from django.urls import path, include

from jazz.views import jazz_home, jazz_add, jazz_detail, jazz_transform, jazz_status

app_name = 'jazz'

urlpatterns = [
    path('', jazz_home, name='jazz'),
    path('jazz_add/', jazz_add, name='jazz_add'),
    path('<int:id>/', jazz_detail, name='jazz_detail'),
    path('<int:id>/transform/', jazz_transform, name='jazz_transform'),
    path('<int:id>/status/', jazz_status, name='jazz_status'),
]
