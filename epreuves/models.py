# epreuves/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

class Classe(models.Model):
    """Classes scolaires de 6ème à Terminale"""
    NIVEAUX = [
        ('6eme', '6ème'),
        ('5eme', '5ème'),
        ('4eme', '4ème'),
        ('3eme', '3ème (BEPC)'),
        ('2nde', 'Seconde'),
        ('1ere', 'Première'),
        ('terminale', 'Terminale (BAC)'),
    ]
    
    nom = models.CharField(max_length=50, choices=NIVEAUX, unique=True)
    niveau_ordre = models.IntegerField(default=0)
    cycle = models.CharField(max_length=20, choices=[
        ('college', 'Collège'),
        ('lycee', 'Lycée')
    ])
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=10, default='📚')
    
    class Meta:
        ordering = ['niveau_ordre']
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
    
    def __str__(self):
        return self.get_nom_display()
    
    def nb_epreuves(self):
        return self.epreuves.count()


class Matiere(models.Model):
    """Matières enseignées"""
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    classes = models.ManyToManyField(Classe, related_name='matieres')
    icone = models.CharField(max_length=10, default='📖')
    couleur = models.CharField(max_length=7, default='#4F46E5')
    
    class Meta:
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class CategorieEpreuve(models.Model):
    """Type d'épreuve"""
    TYPES = [
        ('trimestre1', '1er Trimestre'),
        ('trimestre2', '2ème Trimestre'),
        ('trimestre3', '3ème Trimestre'),
        ('semestre1', '1er Semestre'),
        ('semestre2', '2ème Semestre'),
        ('examen_blanc', 'Examen Blanc'),
        ('revision', 'Fiche de Révision'),
    ]
    
    nom = models.CharField(max_length=50, choices=TYPES)
    
    def __str__(self):
        return self.get_nom_display()


class Epreuve(models.Model):
    """Épreuve scolaire"""
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='epreuves')
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='epreuves')
    categorie = models.ForeignKey(CategorieEpreuve, on_delete=models.SET_NULL, null=True)
    
    annee_scolaire = models.CharField(max_length=9, help_text="Ex: 2024-2025")
    fichier = models.FileField(
        upload_to='epreuves/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    
    # Métadonnées
    duree = models.IntegerField(help_text="Durée en minutes", null=True, blank=True)
    coefficient = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    nombre_pages = models.IntegerField(default=1)
    
    # 🆕 TARIFICATION À L'UNITÉ
    prix_unitaire = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=25,
        help_text="Prix de l'épreuve seule (par défaut 25 FCFA)"
    )
    
    # Gestion des accès
    est_gratuit = models.BooleanField(default=False, help_text="Accessible sans payer ni s'abonner")
    disponible_achat_unitaire = models.BooleanField(default=True, help_text="Peut être acheté à l'unité")
    disponible_abonnement = models.BooleanField(default=True, help_text="Accessible via abonnement")
    
    nombre_telechargements = models.IntegerField(default=0)
    nombre_achats = models.IntegerField(default=0)
    
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_ajout']
        verbose_name = 'Épreuve'
        verbose_name_plural = 'Épreuves'
    
    def __str__(self):
        return f"{self.titre} - {self.classe} - {self.matiere}"
    
    def a_corrige(self):
        return hasattr(self, 'corrige')
    
    def prix_avec_corrige(self):
        """Prix du pack épreuve + corrigé"""
        if self.a_corrige():
            return self.prix_unitaire + self.corrige.prix_unitaire
        return self.prix_unitaire


class Corrige(models.Model):
    """Corrigé d'une épreuve"""
    epreuve = models.OneToOneField(Epreuve, on_delete=models.CASCADE, related_name='corrige')
    fichier = models.FileField(
        upload_to='corriges/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    
    # 🆕 TARIFICATION À L'UNITÉ
    prix_unitaire = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=25,
        help_text="Prix du corrigé seul (par défaut 25 FCFA)"
    )
    
    # Type de corrigé
    TYPE_CHOICES = [
        ('officiel', 'Corrigé Officiel'),
        ('detaille', 'Corrigé Détaillé'),
        ('bareme', 'Barème de Notation'),
    ]
    type_corrige = models.CharField(max_length=20, choices=TYPE_CHOICES, default='detaille')
    
    auteur = models.CharField(max_length=200, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Corrigé - {self.epreuve.titre}"

