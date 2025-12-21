# # epreuves/urls.py
# from django.urls import path
# from . import views

# app_name = 'epreuves'

# urlpatterns = [
#     # Liste et détail
#     path('', views.liste_classes, name='liste_classes'),
#     path('classe/<str:classe_slug>/', views.liste_epreuves, name='liste_epreuves'),
#     path('epreuve/<slug:slug>/', views.detail_epreuve, name='detail'),
    
#     # Téléchargements
#     path('telecharger/epreuve/<slug:slug>/', views.telecharger_epreuve, name='telecharger_epreuve'),
#     path('telecharger/corrige/<slug:slug>/', views.telecharger_corrige, name='telecharger_corrige'),
    
#     # Achats unitaires
#     path('acheter/epreuve/<slug:slug>/', views.acheter_epreuve, name='acheter_epreuve'),
#     path('acheter/corrige/<slug:slug>/', views.acheter_corrige, name='acheter_corrige'),
#     path('acheter/pack/<slug:slug>/', views.acheter_pack, name='acheter_pack'),
    
#     # Traitement paiement
#     path('payer/<slug:slug>/<str:type_achat>/', views.traiter_paiement_unitaire, name='payer'),
#     path('callback/paiement/', views.callback_paiement_unitaire, name='callback_paiement'),
# ]



from django.urls import path
from . import views

app_name = 'epreuves'

urlpatterns = [
    # Pages publiques
    path('', views.liste_classes, name='liste_classes'),
    path('classe/<slug:classe_slug>/', views.liste_epreuves, name='liste_epreuves'),
    
    # Détail épreuve (nécessite connexion)
    path('detail/<slug:slug>/', views.detail_epreuve, name='detail'),
    
    # Téléchargements (nécessite accès)
    path('telecharger/epreuve/<slug:slug>/', views.telecharger_epreuve, name='telecharger_epreuve'),
    path('telecharger/corrige/<slug:slug>/', views.telecharger_corrige, name='telecharger_corrige'),
    
    # Achats unitaires
    path('acheter/epreuve/<slug:slug>/', views.acheter_epreuve, name='acheter_epreuve'),
    path('acheter/corrige/<slug:slug>/', views.acheter_corrige, name='acheter_corrige'),
    path('acheter/pack/<slug:slug>/', views.acheter_pack, name='acheter_pack'),
    
    # Paiement
    path('paiement/<slug:slug>/<str:type_achat>/', views.paiement_unitaire, name='paiement_unitaire'),
]