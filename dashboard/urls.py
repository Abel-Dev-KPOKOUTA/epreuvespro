from django.urls import path 
from .import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('parcourir-epreuves/', views.parcourir_epreuves, name='parcourir_epreuves'),
    path('bibliotheque/', views.bibliotheque, name='bibliotheque'),
    path('mes-telechargements/', views.mes_telechargements, name='mes_telechargements'),
    path('mon-abonnement/', views.mon_abonnement, name='mon_abonnement'),
    path('souscrire/<str:plan_slug>/', views.souscrire_abonnement, name='souscrire_abonnement'),
    path('paiement/<str:plan_slug>/', views.traiter_paiement_abonnement, name='traiter_paiement_abonnement'), 
    path('paiement/callback/', views.callback_paiement, name='callback_paiement'),
]