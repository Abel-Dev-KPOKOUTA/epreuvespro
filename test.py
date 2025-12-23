# Créer les plans d'abonnement
from abonnements.models import PlanAbonnement

# Plan Gratuit
PlanAbonnement.objects.get_or_create(
    type_plan='gratuit',
    defaults={
        'nom': 'Gratuit',
        'prix': 0,
        'limite_telechargements': 3,
        'description': '3 épreuves offertes pour découvrir',
        'ordre': 1,
        'est_actif': True
    }
)

# Plan Mensuel
PlanAbonnement.objects.get_or_create(
    type_plan='mensuel',
    defaults={
        'nom': 'Mensuel',
        'prix': 2500,
        'limite_telechargements': 100,
        'description': '100 téléchargements par mois',
        'ordre': 2,
        'est_actif': True
    }
)

# Plan Annuel
PlanAbonnement.objects.get_or_create(
    type_plan='annuel',
    defaults={
        'nom': 'Annuel',
        'prix': 20000,
        'limite_telechargements': 0,  # Illimité
        'description': 'Téléchargements illimités toute l\'année',
        'ordre': 3,
        'est_actif': True
    }
)

print("✅ Plans d'abonnement créés avec succès !")