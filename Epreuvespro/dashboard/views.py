from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from datetime import datetime, timedelta
from abonnements.models import Telechargement, Abonnement


from django.core.paginator import Paginator
from epreuves.models import Epreuve, Classe, Matiere, CategorieEpreuve

from abonnements.models import AchatUnitaire

from abonnements.models import PlanAbonnement

@login_required
def dashboard_view(request):
    """Vue principale du dashboard"""
    user = request.user
    
    # Statistiques
    total_telechargements = Telechargement.objects.filter(user=user).count()
    telechargements_mois = Telechargement.objects.filter(
        user=user,
        date_telechargement__gte=datetime.now() - timedelta(days=30)
    ).count()
    
    # Abonnement actif
    try:
        abonnement = Abonnement.objects.get(user=user, est_actif=True)
        pourcentage_utilise = 0
        if abonnement.plan.limite_telechargements > 0:
            pourcentage_utilise = (abonnement.telechargements_utilises / abonnement.plan.limite_telechargements) * 100
    except Abonnement.DoesNotExist:
        abonnement = None
        pourcentage_utilise = 0
    
    # Activité récente (derniers téléchargements)
    activites_recentes = Telechargement.objects.filter(user=user).order_by('-date_telechargement')[:5]
    
    # Épreuves disponibles pour sa classe
    from epreuves.models import Epreuve
    epreuves_disponibles = Epreuve.objects.filter(classe__nom__icontains=user.classe).count() if user.classe else 0
    
    context = {
        'total_telechargements': total_telechargements,
        'telechargements_mois': telechargements_mois,
        'abonnement': abonnement,
        'pourcentage_utilise': pourcentage_utilise,
        'activites_recentes': activites_recentes,
        'epreuves_disponibles': epreuves_disponibles,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def parcourir_epreuves(request):
    """Page de parcours des épreuves avec filtres"""
    
    # Récupérer toutes les épreuves
    epreuves = Epreuve.objects.all().select_related('classe', 'matiere', 'categorie')
    
    # FILTRES
    classe_slug = request.GET.get('classe')
    matiere_slug = request.GET.get('matiere')
    categorie_nom = request.GET.get('categorie')
    annee = request.GET.get('annee')
    search = request.GET.get('search')
    
    # Appliquer les filtres
    if classe_slug:
        epreuves = epreuves.filter(classe__nom=classe_slug)
    
    if matiere_slug:
        epreuves = epreuves.filter(matiere__slug=matiere_slug)
    
    if categorie_nom:
        epreuves = epreuves.filter(categorie__nom=categorie_nom)
    
    if annee:
        epreuves = epreuves.filter(annee_scolaire__contains=annee)
    
    if search:
        epreuves = epreuves.filter(
            Q(titre__icontains=search) |
            Q(matiere__nom__icontains=search) |
            Q(classe__nom__icontains=search)
        )
    
    # Tri
    ordre = request.GET.get('ordre', '-date_ajout')
    epreuves = epreuves.order_by(ordre)
    
    # Nombre total avant pagination
    total_epreuves = epreuves.count()
    
    # Pagination (20 épreuves par page)
    paginator = Paginator(epreuves, 20)
    page = request.GET.get('page', 1)
    epreuves_page = paginator.get_page(page)
    
    # Données pour les filtres
    classes = Classe.objects.all()
    matieres = Matiere.objects.all()
    categories = CategorieEpreuve.TYPES
    annees = Epreuve.objects.values_list('annee_scolaire', flat=True).distinct().order_by('-annee_scolaire')
    
    context = {
        'epreuves': epreuves_page,
        'classes': classes,
        'matieres': matieres,
        'categories': categories,
        'annees': annees,
        'total_epreuves': total_epreuves,
        
        # Filtres sélectionnés
        'classe_selectionnee': classe_slug,
        'matiere_selectionnee': matiere_slug,
        'categorie_selectionnee': categorie_nom,
        'annee_selectionnee': annee,
        'search': search,
        'ordre': ordre,
    }
    
    return render(request, 'dashboard/parcourir_epreuves.html', context)



@login_required
def bibliotheque(request):
    """Page bibliothèque - épreuves auxquelles l'utilisateur a accès"""
    user = request.user
    
    # 1. Récupérer toutes les épreuves gratuites
    epreuves_gratuites = Epreuve.objects.filter(est_gratuit=True)
    
    # 2. Récupérer les épreuves achetées à l'unité
    achats = AchatUnitaire.objects.filter(
        user=user,
        type_achat__in=['epreuve', 'pack']
    ).values_list('objet_id', flat=True)
    
    epreuves_achetees = Epreuve.objects.filter(id__in=achats)
    epreuves_achetees_count = len(achats)
    
    # 3. Récupérer les épreuves disponibles via abonnement
    epreuves_abonnement = Epreuve.objects.none()
    abonnement = None
    
    try:
        abonnement = Abonnement.objects.get(user=user, est_actif=True)
        # Vérifier si l'abonnement permet encore de télécharger
        if abonnement.peut_telecharger:
            epreuves_abonnement = Epreuve.objects.filter(disponible_abonnement=True)
    except Abonnement.DoesNotExist:
        pass
    
    # 4. Combiner toutes les épreuves (sans doublons)
    epreuves = (epreuves_gratuites | epreuves_achetees | epreuves_abonnement).distinct()
    
    # 5. Appliquer les filtres
    classe_slug = request.GET.get('classe')
    matiere_slug = request.GET.get('matiere')
    categorie_nom = request.GET.get('categorie')
    search = request.GET.get('search')
    
    if classe_slug:
        epreuves = epreuves.filter(classe__nom=classe_slug)
    
    if matiere_slug:
        epreuves = epreuves.filter(matiere__slug=matiere_slug)
    
    if categorie_nom:
        epreuves = epreuves.filter(categorie__nom=categorie_nom)
    
    if search:
        epreuves = epreuves.filter(
            Q(titre__icontains=search) |
            Q(matiere__nom__icontains=search) |
            Q(classe__nom__icontains=search)
        )
    
    # 6. Tri
    ordre = request.GET.get('ordre', '-date_ajout')
    epreuves = epreuves.order_by(ordre)
    
    # 7. Statistiques (avant pagination)
    total_epreuves = epreuves.count()
    epreuves_gratuites_count = epreuves.filter(est_gratuit=True).count()
    
    # 8. Pagination
    paginator = Paginator(epreuves, 20)
    page = request.GET.get('page', 1)
    epreuves_page = paginator.get_page(page)
    
    # 9. Données pour les filtres
    classes = Classe.objects.all()
    matieres = Matiere.objects.all()
    categories = CategorieEpreuve.TYPES
    
    context = {
        'epreuves': epreuves_page,
        'total_epreuves': total_epreuves,
        'epreuves_gratuites_count': epreuves_gratuites_count,
        'epreuves_achetees_count': epreuves_achetees_count,
        'classes': classes,
        'matieres': matieres,
        'categories': categories,
        'classe_selectionnee': classe_slug,
        'matiere_selectionnee': matiere_slug,
        'categorie_selectionnee': categorie_nom,
        'search': search,
        'ordre': ordre,
        'abonnement': abonnement,
    }
    
    return render(request, 'dashboard/bibliotheque.html', context)






@login_required
def mes_telechargements(request):
    """Page mes téléchargements - historique complet"""
    user = request.user
    
    # Récupérer tous les téléchargements de l'utilisateur
    telechargements = Telechargement.objects.filter(user=user).order_by('-date_telechargement')
    
    # Appliquer les filtres
    type_contenu = request.GET.get('type')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    search = request.GET.get('search')
    
    if type_contenu:
        telechargements = telechargements.filter(type_contenu=type_contenu)
    
    if date_debut:
        from datetime import datetime
        date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')
        telechargements = telechargements.filter(date_telechargement__gte=date_debut_obj)
    
    if date_fin:
        from datetime import datetime
        date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d')
        telechargements = telechargements.filter(date_telechargement__lte=date_fin_obj)
    
    if search:
        telechargements = telechargements.filter(objet_nom__icontains=search)
    
    # Statistiques
    total_telechargements = telechargements.count()
    telechargements_epreuves = telechargements.filter(type_contenu='epreuve').count()
    telechargements_corriges = telechargements.filter(type_contenu='corrige').count()
    telechargements_livres = telechargements.filter(type_contenu='livre').count()
    
    # Téléchargements ce mois
    from datetime import datetime, timedelta
    debut_mois = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    telechargements_ce_mois = Telechargement.objects.filter(
        user=user,
        date_telechargement__gte=debut_mois
    ).count()
    
    # Pagination
    paginator = Paginator(telechargements, 20)
    page = request.GET.get('page', 1)
    telechargements_page = paginator.get_page(page)
    
    # ✨ ENRICHIR LES TÉLÉCHARGEMENTS AVEC LES SLUGS
    for t in telechargements_page:
        if t.type_contenu in ['epreuve', 'corrige']:
            try:
                epreuve = Epreuve.objects.get(id=t.objet_id)
                t.slug = epreuve.slug  # Ajouter le slug dynamiquement
            except Epreuve.DoesNotExist:
                t.slug = None
    
    context = {
        'telechargements': telechargements_page,
        'total_telechargements': total_telechargements,
        'telechargements_epreuves': telechargements_epreuves,
        'telechargements_corriges': telechargements_corriges,
        'telechargements_livres': telechargements_livres,
        'telechargements_ce_mois': telechargements_ce_mois,
        'type_selectionne': type_contenu,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'search': search,
        'types_disponibles': Telechargement.TYPE_CHOICES,
    }
    
    return render(request, 'dashboard/mes_telechargements.html', context)



@login_required
def mon_abonnement(request):
    """Page mon abonnement - gérer son abonnement"""
    user = request.user
    
    # Récupérer l'abonnement actuel
    abonnement = None
    try:
        abonnement = Abonnement.objects.get(user=user, est_actif=True)
    except Abonnement.DoesNotExist:
        pass
    
    # Récupérer tous les plans disponibles
    plans = PlanAbonnement.objects.filter(est_actif=True).order_by('ordre', 'prix')
    
    # Historique des paiements pour abonnements
    from abonnements.models import Paiement
    paiements = Paiement.objects.filter(
        user=user,
        statut='valide'
    ).order_by('-date_paiement')[:10]
    
    # Statistiques d'utilisation
    stats = {}
    if abonnement:
        # Téléchargements ce mois
        from datetime import datetime
        debut_mois = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        telechargements_ce_mois = Telechargement.objects.filter(
            user=user,
            date_telechargement__gte=debut_mois
        ).count()
        
        # Pourcentage d'utilisation
        if abonnement.plan.limite_telechargements > 0:
            pourcentage = (abonnement.telechargements_utilises / abonnement.plan.limite_telechargements) * 100
        else:
            pourcentage = 0  # Illimité
        
        # Jours restants
        from django.utils import timezone
        jours_restants = (abonnement.date_fin - timezone.now()).days
        
        stats = {
            'telechargements_utilises': abonnement.telechargements_utilises,
            'limite_telechargements': abonnement.plan.limite_telechargements,
            'telechargements_restants': max(0, abonnement.plan.limite_telechargements - abonnement.telechargements_utilises) if abonnement.plan.limite_telechargements > 0 else '∞',
            'pourcentage_utilise': pourcentage,
            'jours_restants': max(0, jours_restants),
            'date_renouvellement': abonnement.date_fin,
        }
    
    # Historique des abonnements
    historique_abonnements = Abonnement.objects.filter(user=user).order_by('-date_debut')[:5]
    
    context = {
        'abonnement': abonnement,
        'plans': plans,
        'paiements': paiements,
        'stats': stats,
        'historique_abonnements': historique_abonnements,
    }
    
    return render(request, 'dashboard/mon_abonnement.html', context)