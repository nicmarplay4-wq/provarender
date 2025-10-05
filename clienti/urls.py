from django.urls import path
from . import views

app_name = 'clienti'

urlpatterns = [
    path('prenota/', views.prenota_appuntamento, name='prenota'),
    path('successo/', views.appuntamento_successo, name='appuntamento_successo'),
]
