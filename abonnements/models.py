from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal

class PlanAbonnement(models.Model):
    """Plans d'abonnement disponibles"""
    
    TYPE_CHOICES = [
        ('gratuit', 'Gratuit'),
        ('mensuel', 'Mensuel'),
        ('annuel', 'Annuel'),
    ]
    
    nom = models.CharField(max_length=100, verbose_name="Nom du plan")
    type_plan = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)
    prix = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix"
    )
    limite_telechargements = models.IntegerField(
        default=0, 
        help_text="0 = illimité",
        verbose_name="Limite de téléchargements"
    )
    description = models.TextField(blank=True, null=True)
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    ordre = models.IntegerField(default=0, help_text="Ordre d'affichage")
    
    class Meta:
        verbose_name = "Plan d'abonnement"
        verbose_name_plural = "Plans d'abonnement"
        ordering = ['ordre', 'prix']
    
    def __str__(self):
        return f"{self.nom} - {self.prix} FCFA"


class Abonnement(models.Model):
    """Abonnements des utilisateurs"""
    
    # IMPORTANT: Utilise settings.AUTH_USER_MODEL au lieu de User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # ← Changement ici
        on_delete=models.CASCADE,
        related_name='abonnement',
        verbose_name="Utilisateur"
    )
    plan = models.ForeignKey(
        PlanAbonnement,
        on_delete=models.PROTECT,
        related_name='abonnements',
        verbose_name="Plan"
    )
    date_debut = models.DateTimeField(auto_now_add=True, verbose_name="Date de début")
    date_fin = models.DateTimeField(verbose_name="Date de fin")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    renouvellement_auto = models.BooleanField(default=False, verbose_name="Renouvellement automatique")
    telechargements_utilises = models.IntegerField(
        default=0,
        verbose_name="Téléchargements utilisés ce mois"
    )
    
    class Meta:
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.nom}"
    
    @property
    def peut_telecharger(self):
        """Vérifie si l'utilisateur peut encore télécharger"""
        if not self.est_actif:
            return False
        if self.plan.limite_telechargements == 0:  # Illimité
            return True
        return self.telechargements_utilises < self.plan.limite_telechargements


class Paiement(models.Model):
    """Historique des paiements"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('echoue', 'Échoué'),
        ('rembourse', 'Remboursé'),
    ]
    
    METHODE_CHOICES = [
        ('fedapay', 'FedaPay'),
        ('kkiapay', 'KKiaPay'),
        ('moov_money', 'Moov Money'),
        ('mtn_mobile', 'MTN Mobile Money'),
    ]
    
    # IMPORTANT: Utilise settings.AUTH_USER_MODEL
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← Changement ici
        on_delete=models.CASCADE,
        related_name='paiements',
        verbose_name="Utilisateur"
    )
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Montant"
    )
    methode = models.CharField(
        max_length=50,
        choices=METHODE_CHOICES,
        verbose_name="Méthode de paiement"
    )
    reference = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Référence de transaction"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut"
    )
    transaction_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="ID de transaction externe"
    )
    date_paiement = models.DateTimeField(auto_now_add=True, verbose_name="Date de paiement")
    date_validation = models.DateTimeField(blank=True, null=True, verbose_name="Date de validation")
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']
    
    def __str__(self):
        return f"{self.user.email} - {self.montant} FCFA - {self.get_statut_display()}"


class AchatUnitaire(models.Model):
    """Achats unitaires (épreuves/corrigés/livres)"""
    
    TYPE_CHOICES = [
        ('epreuve', 'Épreuve'),
        ('corrige', 'Corrigé'),
        ('pack', 'Pack (Épreuve + Corrigé)'),
        ('livre', 'Livre'),
    ]
    
    # IMPORTANT: Utilise settings.AUTH_USER_MODEL
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← Changement ici
        on_delete=models.CASCADE,
        related_name='achats_unitaires',
        verbose_name="Utilisateur"
    )
    type_achat = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Type d'achat"
    )
    objet_id = models.IntegerField(
        verbose_name="ID de l'objet acheté",
        help_text="ID de l'épreuve, corrigé ou livre"
    )
    objet_nom = models.CharField(
        max_length=255,
        verbose_name="Nom de l'objet"
    )
    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Prix payé"
    )
    paiement = models.ForeignKey(
        Paiement,
        on_delete=models.CASCADE,
        related_name='achats',
        verbose_name="Paiement associé"
    )
    date_achat = models.DateTimeField(auto_now_add=True, verbose_name="Date d'achat")
    
    class Meta:
        verbose_name = "Achat unitaire"
        verbose_name_plural = "Achats unitaires"
        ordering = ['-date_achat']
        unique_together = ['user', 'type_achat', 'objet_id']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_type_achat_display()} - {self.objet_nom}"


class Telechargement(models.Model):
    """Historique des téléchargements"""
    
    TYPE_CHOICES = [
        ('epreuve', 'Épreuve'),
        ('corrige', 'Corrigé'),
        ('livre', 'Livre'),
    ]
    
    # IMPORTANT: Utilise settings.AUTH_USER_MODEL
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← Changement ici
        on_delete=models.CASCADE,
        related_name='telechargements',
        verbose_name="Utilisateur"
    )
    type_contenu = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Type de contenu"
    )
    objet_id = models.IntegerField(verbose_name="ID de l'objet téléchargé")
    objet_nom = models.CharField(max_length=255, verbose_name="Nom de l'objet")
    date_telechargement = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de téléchargement"
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="Adresse IP"
    )
    
    class Meta:
        verbose_name = "Téléchargement"
        verbose_name_plural = "Téléchargements"
        ordering = ['-date_telechargement']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_type_contenu_display()} - {self.objet_nom}"
    




