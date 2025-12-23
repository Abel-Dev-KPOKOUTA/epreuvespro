from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.contrib import messages
from django.utils import timezone

from Epreuvespro import settings
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
        'fedaPay_public_key': settings.FEDAPAY_PUBLIC_KEY,
        'kkiapay_public_key': settings.FEDAPAY_SECRET_KEY,
    }
    
    return render(request, 'epreuves/paiement_unitaire.html', context)



@login_required
def callback_paiement_unitaire(request):
    """Callback après paiement FedaPay pour achat unitaire"""
    from abonnements.models import Paiement, AchatUnitaire
    from abonnements.services.fedapay_service import FedaPayService
    from django.utils import timezone
    
    # Récupérer les paramètres
    transaction_id = request.GET.get('id')  # FedaPay renvoie 'id'
    
    if not transaction_id:
        messages.error(request, "❌ Erreur : Transaction introuvable.")
        return redirect('dashboard:dashboard')
    
    # Récupérer le paiement
    paiement_id = request.session.get('paiement_id')
    
    try:
        paiement = Paiement.objects.get(id=paiement_id, transaction_id=transaction_id)
    except Paiement.DoesNotExist:
        try:
            paiement = Paiement.objects.get(transaction_id=transaction_id)
        except Paiement.DoesNotExist:
            messages.error(request, "❌ Paiement introuvable.")
            return redirect('dashboard:dashboard')
    
    # Vérifier le statut auprès de FedaPay
    fedapay_service = FedaPayService()
    result = fedapay_service.verifier_transaction(transaction_id)
    
    if not result['success']:
        messages.error(request, f"❌ Erreur lors de la vérification : {result.get('error')}")
        return redirect('dashboard:dashboard')
    
    # Récupérer les infos de la session
    epreuve_slug = request.session.get('epreuve_slug')
    type_achat = request.session.get('type_achat')
    
    epreuve = get_object_or_404(Epreuve, slug=epreuve_slug)
    
    # Traiter selon le statut
    if result['status'] == 'approved':
        paiement.statut = 'valide'
        paiement.date_validation = timezone.now()
        paiement.save()
        
        # Créer l'achat unitaire
        AchatUnitaire.objects.create(
            user=paiement.user,
            type_achat=type_achat,
            objet_id=epreuve.id,
            objet_nom=epreuve.titre,
            prix=paiement.montant,
            paiement=paiement
        )
        
        # Incrémenter le compteur
        epreuve.nombre_achats += 1
        epreuve.save()
        
        # Nettoyer la session
        request.session.pop('paiement_id', None)
        request.session.pop('epreuve_slug', None)
        request.session.pop('type_achat', None)
        
        messages.success(request, f"🎉 Paiement de {paiement.montant} FCFA réussi ! Vous pouvez maintenant télécharger votre contenu.")
        return redirect('epreuves:detail', slug=epreuve_slug)
    
    elif result['status'] == 'declined':
        paiement.statut = 'echoue'
        paiement.save()
        messages.error(request, "❌ Le paiement a été refusé. Veuillez réessayer.")
        return redirect('epreuves:detail', slug=epreuve_slug)
    
    elif result['status'] == 'canceled':
        paiement.statut = 'echoue'
        paiement.save()
        messages.warning(request, "⚠️ Le paiement a été annulé.")
        return redirect('epreuves:detail', slug=epreuve_slug)
    
    else:  # pending
        messages.info(request, "⏳ Paiement en cours de traitement. Nous vous notifierons dès confirmation.")
        return redirect('epreuves:detail', slug=epreuve_slug)

