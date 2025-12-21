from django.urls import path 
from .import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('parcourir-epreuves/', views.parcourir_epreuves, name='parcourir_epreuves'),
    path('bibliotheque/', views.bibliotheque, name='bibliotheque'),
    path('mes-telechargements/', views.mes_telechargements, name='mes_telechargements'),
    path('mon-abonnement/', views.mon_abonnement, name='mon_abonnement'),
]