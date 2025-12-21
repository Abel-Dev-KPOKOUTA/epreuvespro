# # epreuves/views.py
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.http import FileResponse, Http404
# from django.contrib import messages
# from django.utils import timezone
# from .models import Epreuve, Corrige
# from abonnements.models import Telechargement
# from abonnements.models import Abonnement, AchatUnitaire

# # ============================================
# # LOGIQUE DE VÉRIFICATION D'ACCÈS
# # ============================================

# def verifier_acces_epreuve(user, epreuve):
#     """
#     Vérifie si l'utilisateur peut accéder à une épreuve
#     Retourne: (peut_acceder: bool, raison: str, source: str)
#     """
#     # 1. Vérifier si l'épreuve est gratuite
#     if epreuve.est_gratuit:
#         return True, "Épreuve gratuite", "gratuit"
    
#     # 2. Vérifier si l'utilisateur a acheté cette épreuve
#     achat = AchatUnitaire.objects.filter(
#         user=user,
#         epreuve=epreuve,
#         paiement__statut='reussi'
#     ).first()
    
#     if achat:
#         # Vérifier si l'achat n'est pas expiré (si une date d'expiration existe)
#         if achat.date_expiration is None or timezone.now() < achat.date_expiration:
#             return True, "Épreuve déjà achetée", "achat_unitaire"
    
#     # 3. Vérifier si l'utilisateur a un abonnement actif
#     if epreuve.disponible_abonnement:
#         try:
#             abonnement = user.abonnement
#             if abonnement.est_actif and not abonnement.est_expire():
#                 if abonnement.telechargements_restants > 0:
#                     return True, "Abonnement actif", "abonnement"
#                 else:
#                     return False, "Téléchargements épuisés", None
#         except Abonnement.DoesNotExist:
#             pass
    
#     # 4. Aucun accès disponible
#     return False, "Paiement requis", None


# def verifier_acces_corrige(user, corrige):
#     """
#     Vérifie si l'utilisateur peut accéder à un corrigé
#     """
#     # 1. Vérifier si l'utilisateur a acheté le corrigé seul
#     achat_corrige = AchatUnitaire.objects.filter(
#         user=user,
#         corrige=corrige,
#         paiement__statut='reussi'
#     ).first()
    
#     if achat_corrige:
#         return True, "Corrigé acheté", "achat_unitaire"
    
#     # 2. Vérifier si l'utilisateur a acheté le pack épreuve+corrigé
#     achat_pack = AchatUnitaire.objects.filter(
#         user=user,
#         epreuve=corrige.epreuve,
#         est_pack=True,
#         paiement__statut='reussi'
#     ).first()
    
#     if achat_pack:
#         return True, "Pack acheté", "achat_unitaire"
    
#     # 3. Vérifier l'abonnement
#     try:
#         abonnement = user.abonnement
#         if abonnement.est_actif and not abonnement.est_expire():
#             if abonnement.plan.acces_corriges:
#                 if abonnement.telechargements_restants > 0:
#                     return True, "Abonnement avec accès corrigés", "abonnement"
#     except Abonnement.DoesNotExist:
#         pass
    
#     return False, "Paiement requis", None


# # ============================================
# # VUES DE TÉLÉCHARGEMENT
# # ============================================

# @login_required
# def telecharger_epreuve(request, slug):
#     """Télécharger une épreuve"""
#     epreuve = get_object_or_404(Epreuve, slug=slug)
    
#     # Vérifier l'accès
#     peut_acceder, raison, source = verifier_acces_epreuve(request.user, epreuve)
    
#     if not peut_acceder:
#         if raison == "Téléchargements épuisés":
#             messages.warning(request, "⚠️ Tu as épuisé tes téléchargements du mois. Renouvelle ton abonnement ou achète cette épreuve à l'unité !")
#         else:
#             messages.info(request, f"💰 Cette épreuve coûte {epreuve.prix_unitaire} FCFA. Achète-la maintenant !")
#         return redirect('epreuves:detail', slug=slug)
    
#     # Gérer selon la source d'accès
#     if source == "abonnement":
#         # Décrémenter les téléchargements
#         abonnement = request.user.abonnement
#         abonnement.telechargements_restants -= 1
#         abonnement.save()
#         messages.success(request, f"✅ Téléchargement via abonnement. {abonnement.telechargements_restants} restants.")
    
#     # Enregistrer le téléchargement
#     telechargement = Telechargement.objects.create(
#         user=request.user,
#         epreuve=epreuve,
#         source=source,
#         adresse_ip=_get_client_ip(request)
#     )
    
#     # Incrémenter le compteur
#     epreuve.nombre_telechargements += 1
#     epreuve.save()
    
#     return _servir_fichier(request, epreuve.fichier, epreuve, 'epreuve')


# @login_required
# def telecharger_corrige(request, slug):
#     """Télécharger un corrigé"""
#     epreuve = get_object_or_404(Epreuve, slug=slug)
    
#     if not epreuve.a_corrige():
#         messages.warning(request, "⚠️ Le corrigé n'est pas encore disponible.")
#         return redirect('epreuves:detail', slug=slug)
    
#     corrige = epreuve.corrige
    
#     # Vérifier l'accès
#     peut_acceder, raison, source = verifier_acces_corrige(request.user, corrige)
    
#     if not peut_acceder:
#         messages.info(request, f"💰 Ce corrigé coûte {corrige.prix_unitaire} FCFA. Achète-le maintenant !")
#         return redirect('epreuves:detail', slug=slug)
    
#     # Gérer selon la source
#     if source == "abonnement":
#         abonnement = request.user.abonnement
#         abonnement.telechargements_restants -= 1
#         abonnement.save()
    
#     # Enregistrer le téléchargement
#     Telechargement.objects.create(
#         user=request.user,
#         corrige=corrige,
#         source=source,
#         adresse_ip=_get_client_ip(request)
#     )
    
#     return _servir_fichier(request, corrige.fichier, epreuve, 'corrige')


# # ============================================
# # VUES D'ACHAT À L'UNITÉ
# # ============================================

# @login_required
# def acheter_epreuve(request, slug):
#     """Page d'achat d'une épreuve seule"""
#     epreuve = get_object_or_404(Epreuve, slug=slug)
    
#     # Vérifier si déjà acheté
#     achat_existant = AchatUnitaire.objects.filter(
#         user=request.user,
#         epreuve=epreuve,
#         paiement__statut='reussi'
#     ).exists()
    
#     if achat_existant:
#         messages.info(request, "✅ Tu as déjà acheté cette épreuve ! Télécharge-la directement.")
#         return redirect('epreuves:detail', slug=slug)
    
#     context = {
#         'epreuve': epreuve,
#         'prix': epreuve.prix_unitaire,
#         'type_achat': 'epreuve',
#     }
#     return render(request, 'epreuves/acheter.html', context)


# @login_required
# def acheter_corrige(request, slug):
#     """Page d'achat d'un corrigé seul"""
#     epreuve = get_object_or_404(Epreuve, slug=slug)
    
#     if not epreuve.a_corrige():
#         messages.error(request, "❌ Ce corrigé n'existe pas encore.")
#         return redirect('epreuves:detail', slug=slug)
    
#     corrige = epreuve.corrige
    
#     # Vérifier si déjà acheté
#     achat_existant = AchatUnitaire.objects.filter(
#         user=request.user,
#         corrige=corrige,
#         paiement__statut='reussi'
#     ).exists()
    
#     if achat_existant:
#         messages.info(request, "✅ Tu as déjà acheté ce corrigé !")
#         return redirect('epreuves:detail', slug=slug)
    
#     context = {
#         'epreuve': epreuve,
#         'corrige': corrige,
#         'prix': corrige.prix_unitaire,
#         'type_achat': 'corrige',
#     }
#     return render(request, 'epreuves/acheter.html', context)


# @login_required
# def acheter_pack(request, slug):
#     """Page d'achat du pack épreuve + corrigé"""
#     epreuve = get_object_or_404(Epreuve, slug=slug)
    
#     if not epreuve.a_corrige():
#         messages.error(request, "❌ Le pack n'est pas disponible sans corrigé.")
#         return redirect('epreuves:acheter_epreuve', slug=slug)
    
#     # Vérifier si déjà acheté
#     achat_existant = AchatUnitaire.objects.filter(
#         user=request.user,
#         epreuve=epreuve,
#         est_pack=True,
#         paiement__statut='reussi'
#     ).exists()
    
#     if achat_existant:
#         messages.info(request, "✅ Tu as déjà acheté ce pack !")
#         return redirect('epreuves:detail', slug=slug)
    
#     context = {
#         'epreuve': epreuve,
#         'corrige': epreuve.corrige,
#         'prix': epreuve.prix_avec_corrige(),
#         'type_achat': 'pack',
#         'economie': (epreuve.prix_unitaire + epreuve.corrige.prix_unitaire) - epreuve.prix_avec_corrige()
#     }
#     return render(request, 'epreuves/acheter.html', context)


# # ============================================
# # TRAITEMENT DU PAIEMENT
# # ============================================

# @login_required
# def traiter_paiement_unitaire(request, slug, type_achat):
#     """
#     Initier le paiement via Kkiapay pour un achat unitaire
#     type_achat: 'epreuve', 'corrige', ou 'pack'
#     """
#     import uuid
#     from abonnements.models import Paiement
    
#     epreuve = get_object_or_404(Epreuve, slug=slug)
    
#     # Déterminer le prix et ce qui est acheté
#     if type_achat == 'epreuve':
#         montant = epreuve.prix_unitaire
#         type_paiement = 'epreuve'
#     elif type_achat == 'corrige':
#         if not epreuve.a_corrige():
#             messages.error(request, "❌ Corrigé non disponible.")
#             return redirect('epreuves:detail', slug=slug)
#         montant = epreuve.corrige.prix_unitaire
#         type_paiement = 'corrige'
#     elif type_achat == 'pack':
#         if not epreuve.a_corrige():
#             messages.error(request, "❌ Pack non disponible.")
#             return redirect('epreuves:detail', slug=slug)
#         montant = epreuve.prix_avec_corrige()
#         type_paiement = 'pack'
#     else:
#         messages.error(request, "❌ Type d'achat invalide.")
#         return redirect('epreuves:detail', slug=slug)
    
#     # Créer la référence de paiement
#     reference = f"UNIT-{uuid.uuid4().hex[:10].upper()}"
    
#     # Créer l'enregistrement de paiement
#     paiement = Paiement.objects.create(
#         user=request.user,
#         type_paiement=type_paiement,
#         montant=montant,
#         methode='kkiapay',
#         reference=reference,
#         statut='en_attente',
#         epreuve=epreuve if type_achat in ['epreuve', 'pack'] else None,
#         corrige=epreuve.corrige if type_achat in ['corrige', 'pack'] else None,
#     )
    
#     # Préparer les données pour Kkiapay
#     from django.conf import settings
#     context = {
#         'epreuve': epreuve,
#         'type_achat': type_achat,
#         'montant': float(montant),
#         'reference': reference,
#         'paiement_id': paiement.id,
#         'kkiapay_public_key': settings.KKIAPAY_PUBLIC_KEY,
#     }
    
#     return render(request, 'epreuves/paiement_kkiapay.html', context)


# @login_required
# def callback_paiement_unitaire(request):
#     """Callback après paiement Kkiapay pour achat unitaire"""
#     transaction_id = request.GET.get('transaction_id')
#     reference = request.GET.get('reference')
    
#     if not transaction_id or not reference:
#         messages.error(request, "❌ Erreur lors du paiement.")
#         return redirect('core:accueil')
    
#     # Récupérer le paiement
#     try:
#         paiement = Paiement.objects.get(reference=reference)
#     except Paiement.DoesNotExist:
#         messages.error(request, "❌ Paiement introuvable.")
#         return redirect('core:accueil')
    
#     # TODO: Vérifier le statut du paiement auprès de Kkiapay API
#     # Pour l'instant, on suppose que c'est réussi
    
#     paiement.statut = 'reussi'
#     paiement.transaction_id = transaction_id
#     paiement.date_validation = timezone.now()
#     paiement.save()
    
#     # Créer l'achat unitaire
#     achat = AchatUnitaire.objects.create(
#         user=request.user,
#         paiement=paiement,
#         epreuve=paiement.epreuve if paiement.type_paiement in ['epreuve', 'pack'] else None,
#         corrige=paiement.corrige if paiement.type_paiement == 'corrige' else None,
#         est_pack=(paiement.type_paiement == 'pack')
#     )
    
#     # Incrémenter le compteur d'achats
#     if paiement.epreuve:
#         paiement.epreuve.nombre_achats += 1
#         paiement.epreuve.save()
    
#     messages.success(request, f"✅ Paiement de {paiement.montant} FCFA réussi ! Tu peux maintenant télécharger.")
    
#     return redirect('epreuves:detail', slug=paiement.epreuve.slug)


# # ============================================
# # UTILITAIRES
# # ============================================

# def _servir_fichier(request, fichier, epreuve, type_fichier):
#     """Servir un fichier PDF de manière sécurisée"""
#     try:
#         response = FileResponse(fichier.open('rb'), content_type='application/pdf')
#         filename = f"{epreuve.titre}_{type_fichier}.pdf"
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         return response
#     except FileNotFoundError:
#         raise Http404("❌ Fichier introuvable.")


# def _get_client_ip(request):
#     """Récupérer l'IP du client"""
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip


# # ============================================
# # PAGE DÉTAIL ÉPREUVE
# # ============================================

# def detail_epreuve(request, slug):
#     """Page de détail d'une épreuve avec options d'achat"""
#     epreuve = get_object_or_404(Epreuve, slug=slug)
    
#     # Vérifier les accès de l'utilisateur
#     peut_telecharger_epreuve = False
#     peut_telecharger_corrige = False
#     source_acces = None
    
#     if request.user.is_authenticated:
#         peut_telecharger_epreuve, _, source = verifier_acces_epreuve(request.user, epreuve)
#         source_acces = source
        
#         if epreuve.a_corrige():
#             peut_telecharger_corrige, _, _ = verifier_acces_corrige(request.user, epreuve.corrige)
    
#     context = {
#         'epreuve': epreuve,
#         'peut_telecharger_epreuve': peut_telecharger_epreuve,
#         'peut_telecharger_corrige': peut_telecharger_corrige,
#         'source_acces': source_acces,
#     }
#     return render(request, 'epreuves/detail_epreuve.html', context)




# def liste_classes(request):
#     """Liste des classes avec épreuves disponibles"""
#     from epreuves.models import Classe
#     classes = Classe.objects.filter(epreuves__isnull=False).distinct()
#     context = {
#         'classes': classes,
#     }
#     return render(request, 'epreuves/liste_classes.html', context)


# def liste_epreuves(request, classe_slug):
#     """Liste des épreuves pour une classe donnée"""
#     from epreuves.models import Classe
#     classe = get_object_or_404(Classe, slug=classe_slug)
#     epreuves = classe.epreuves.all()
#     context = {
#         'classe': classe,
#         'epreuves': epreuves,
#     }
#     return render(request, 'epreuves/liste_epreuves.html', context)




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.contrib import messages
from django.utils import timezone
from .models import Epreuve, Corrige
from abonnements.models import Telechargement, Abonnement, AchatUnitaire

# ============================================
# LOGIQUE DE VÉRIFICATION D'ACCÈS - ADAPTÉE
# ============================================

def verifier_acces_epreuve(user, epreuve):
    """
    Vérifie si l'utilisateur peut accéder à une épreuve
    Retourne: (peut_acceder: bool, via_abonnement: bool)
    """
    # 1. Vérifier si l'épreuve est gratuite
    if epreuve.est_gratuit:
        return True, False
    
    # 2. Vérifier si l'utilisateur a acheté cette épreuve ou le pack
    achat = AchatUnitaire.objects.filter(
        user=user,
        objet_id=epreuve.id,
        type_achat__in=['epreuve', 'pack']
    ).exists()
    
    if achat:
        return True, False
    
    # 3. Vérifier si l'utilisateur a un abonnement actif
    if epreuve.disponible_abonnement:
        try:
            abonnement = Abonnement.objects.get(user=user, est_actif=True)
            if abonnement.peut_telecharger:
                return True, True
        except Abonnement.DoesNotExist:
            pass
    
    # 4. Aucun accès disponible
    return False, False


def verifier_acces_corrige(user, epreuve):
    """
    Vérifie si l'utilisateur peut accéder au corrigé d'une épreuve
    """
    if not epreuve.a_corrige():
        return False, False
    
    # 1. Vérifier si l'épreuve est gratuite
    if epreuve.est_gratuit:
        return True, False
    
    # 2. Vérifier si l'utilisateur a acheté le corrigé ou le pack
    achat = AchatUnitaire.objects.filter(
        user=user,
        objet_id=epreuve.id,
        type_achat__in=['corrige', 'pack']
    ).exists()
    
    if achat:
        return True, False
    
    # 3. Vérifier l'abonnement
    if epreuve.disponible_abonnement:
        try:
            abonnement = Abonnement.objects.get(user=user, est_actif=True)
            if abonnement.peut_telecharger:
                return True, True
        except Abonnement.DoesNotExist:
            pass
    
    return False, False


# ============================================
# PAGE DÉTAIL ÉPREUVE - VERSION AMÉLIORÉE
# ============================================

@login_required
def detail_epreuve(request, slug):
    """Page de détail d'une épreuve avec options d'achat"""
    epreuve = get_object_or_404(Epreuve, slug=slug)
    
    # Vérifier les accès de l'utilisateur
    peut_telecharger_epreuve, via_abonnement_epreuve = verifier_acces_epreuve(request.user, epreuve)
    peut_telecharger_corrige, via_abonnement_corrige = verifier_acces_corrige(request.user, epreuve)
    
    # Déterminer le statut global
    a_acces_epreuve = peut_telecharger_epreuve or epreuve.est_gratuit
    a_acces_corrige = peut_telecharger_corrige or epreuve.est_gratuit
    
    # Calculer le prix du pack
    prix_pack = None
    if epreuve.a_corrige():
        prix_pack = epreuve.prix_unitaire + epreuve.corrige.prix_unitaire
    
    # Option sélectionnée par défaut
    selected_option = request.GET.get('option', 'pack' if epreuve.a_corrige() else 'epreuve')
    
    # Récupérer l'abonnement pour afficher les infos
    abonnement = None
    try:
        abonnement = Abonnement.objects.get(user=request.user, est_actif=True)
    except Abonnement.DoesNotExist:
        pass
    
    context = {
        'epreuve': epreuve,
        'a_acces_epreuve': a_acces_epreuve,
        'a_acces_corrige': a_acces_corrige,
        'via_abonnement': via_abonnement_epreuve or via_abonnement_corrige,
        'prix_pack': prix_pack,
        'selected_option': selected_option,
        'abonnement': abonnement,
    }
    
    return render(request, 'epreuves/detail_epreuve.html', context)


# ============================================
# VUES DE TÉLÉCHARGEMENT - ADAPTÉES
# ============================================

@login_required
def telecharger_epreuve(request, slug):
    """Télécharger une épreuve"""
    epreuve = get_object_or_404(Epreuve, slug=slug)
    
    # Vérifier l'accès
    peut_acceder, via_abonnement = verifier_acces_epreuve(request.user, epreuve)
    
    if not peut_acceder and not epreuve.est_gratuit:
        messages.warning(request, f"💰 Cette épreuve coûte {epreuve.prix_unitaire} FCFA. Achète-la maintenant !")
        return redirect('epreuves:detail', slug=slug)
    
    # Gérer selon la source d'accès
    if via_abonnement:
        # Décrémenter les téléchargements
        try:
            abonnement = Abonnement.objects.get(user=request.user, est_actif=True)
            abonnement.telechargements_utilises += 1
            abonnement.save()
            messages.success(request, f"✅ Téléchargement via abonnement.")
        except Abonnement.DoesNotExist:
            pass
    
    # Enregistrer le téléchargement
    Telechargement.objects.create(
        user=request.user,
        type_contenu='epreuve',
        objet_id=epreuve.id,
        objet_nom=epreuve.titre,
        ip_address=_get_client_ip(request)
    )
    
    # Incrémenter le compteur
    epreuve.nombre_telechargements += 1
    epreuve.save()
    
    return _servir_fichier(request, epreuve.fichier, epreuve, 'epreuve')


@login_required
def telecharger_corrige(request, slug):
    """Télécharger un corrigé"""
    epreuve = get_object_or_404(Epreuve, slug=slug)
    
    if not epreuve.a_corrige():
        messages.warning(request, "⚠️ Le corrigé n'est pas encore disponible.")
        return redirect('epreuves:detail', slug=slug)
    
    # Vérifier l'accès
    peut_acceder, via_abonnement = verifier_acces_corrige(request.user, epreuve)
    
    if not peut_acceder and not epreuve.est_gratuit:
        messages.warning(request, f"💰 Ce corrigé coûte {epreuve.corrige.prix_unitaire} FCFA. Achète-le maintenant !")
        return redirect('epreuves:detail', slug=slug)
    
    # Gérer selon la source
    if via_abonnement:
        try:
            abonnement = Abonnement.objects.get(user=request.user, est_actif=True)
            abonnement.telechargements_utilises += 1
            abonnement.save()
        except Abonnement.DoesNotExist:
            pass
    
    # Enregistrer le téléchargement
    Telechargement.objects.create(
        user=request.user,
        type_contenu='corrige',
        objet_id=epreuve.id,
        objet_nom=f"Corrigé - {epreuve.titre}",
        ip_address=_get_client_ip(request)
    )
    
    return _servir_fichier(request, epreuve.corrige.fichier, epreuve, 'corrige')


# ============================================
# VUES D'ACHAT À L'UNITÉ - SIMPLIFIÉES
# ============================================

@login_required
def acheter_epreuve(request, slug):
    """Acheter une épreuve seule"""
    epreuve = get_object_or_404(Epreuve, slug=slug)
    
    # Vérifier si déjà acheté ou accessible
    peut_acceder, _ = verifier_acces_epreuve(request.user, epreuve)
    if peut_acceder:
        messages.info(request, "✅ Vous avez déjà accès à cette épreuve !")
        return redirect('epreuves:detail', slug=slug)
    
    # Rediriger vers le paiement
    return redirect('epreuves:paiement_unitaire', slug=slug, type_achat='epreuve')


@login_required
def acheter_corrige(request, slug):
    """Acheter un corrigé seul"""
    epreuve = get_object_or_404(Epreuve, slug=slug)
    
    if not epreuve.a_corrige():
        messages.error(request, "❌ Ce corrigé n'existe pas encore.")
        return redirect('epreuves:detail', slug=slug)
    
    # Vérifier si déjà acheté ou accessible
    peut_acceder, _ = verifier_acces_corrige(request.user, epreuve)
    if peut_acceder:
        messages.info(request, "✅ Vous avez déjà accès à ce corrigé !")
        return redirect('epreuves:detail', slug=slug)
    
    # Rediriger vers le paiement
    return redirect('epreuves:paiement_unitaire', slug=slug, type_achat='corrige')


@login_required
def acheter_pack(request, slug):
    """Acheter le pack épreuve + corrigé"""
    epreuve = get_object_or_404(Epreuve, slug=slug)
    
    if not epreuve.a_corrige():
        messages.error(request, "❌ Le pack n'est pas disponible sans corrigé.")
        return redirect('epreuves:acheter_epreuve', slug=slug)
    
    # Vérifier si déjà acheté
    achat = AchatUnitaire.objects.filter(
        user=request.user,
        objet_id=epreuve.id,
        type_achat='pack'
    ).exists()
    
    if achat:
        messages.info(request, "✅ Vous avez déjà acheté ce pack !")
        return redirect('epreuves:detail', slug=slug)
    
    # Rediriger vers le paiement
    return redirect('epreuves:paiement_unitaire', slug=slug, type_achat='pack')


# ============================================
# UTILITAIRES
# ============================================

def _servir_fichier(request, fichier, epreuve, type_fichier):
    """Servir un fichier PDF de manière sécurisée"""
    try:
        response = FileResponse(fichier.open('rb'), content_type='application/pdf')
        filename = f"{epreuve.titre}_{type_fichier}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except FileNotFoundError:
        raise Http404("❌ Fichier introuvable.")


def _get_client_ip(request):
    """Récupérer l'IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ============================================
# VUES PUBLIQUES
# ============================================

def liste_classes(request):
    """Liste des classes avec épreuves disponibles"""
    from epreuves.models import Classe
    classes = Classe.objects.filter(epreuves__isnull=False).distinct()
    context = {
        'classes': classes,
    }
    return render(request, 'epreuves/liste_classes.html', context)


def liste_epreuves(request, classe_slug):
    """Liste des épreuves pour une classe donnée"""
    from epreuves.models import Classe
    classe = get_object_or_404(Classe, slug=classe_slug)
    epreuves = classe.epreuves.filter(est_actif=True).order_by('-date_ajout')
    context = {
        'classe': classe,
        'epreuves': epreuves,
    }
    return render(request, 'epreuves/liste_epreuves.html', context)


# ============================================
# VUE DE PAIEMENT SIMPLIFIÉE (à adapter avec FedaPay/KKiaPay)
# ============================================

@login_required
def paiement_unitaire(request, slug, type_achat):
    """
    Page de paiement pour achat unitaire
    type_achat: 'epreuve', 'corrige', ou 'pack'
    """
    epreuve = get_object_or_404(Epreuve, slug=slug)
    
    # Déterminer le prix
    if type_achat == 'epreuve':
        montant = epreuve.prix_unitaire
        description = f"Achat épreuve: {epreuve.titre}"
    elif type_achat == 'corrige':
        if not epreuve.a_corrige():
            messages.error(request, "❌ Corrigé non disponible.")
            return redirect('epreuves:detail', slug=slug)
        montant = epreuve.corrige.prix_unitaire
        description = f"Achat corrigé: {epreuve.titre}"
    elif type_achat == 'pack':
        if not epreuve.a_corrige():
            messages.error(request, "❌ Pack non disponible.")
            return redirect('epreuves:detail', slug=slug)
        montant = epreuve.prix_unitaire + epreuve.corrige.prix_unitaire
        description = f"Achat pack: {epreuve.titre}"
    else:
        messages.error(request, "❌ Type d'achat invalide.")
        return redirect('epreuves:detail', slug=slug)
    
    context = {
        'epreuve': epreuve,
        'type_achat': type_achat,
        'montant': montant,
        'description': description,
        # À ajouter : clés API FedaPay/KKiaPay
        'fedaPay_public_key': 'YOUR_FEDAPAY_PUBLIC_KEY',
        'kkiapay_public_key': 'YOUR_KKIAPAY_PUBLIC_KEY',
    }
    
    return render(request, 'epreuves/paiement_unitaire.html', context)


