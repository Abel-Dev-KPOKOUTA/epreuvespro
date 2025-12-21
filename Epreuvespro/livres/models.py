from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from epreuves.models import Classe

class CategorieLivre(models.Model):
    """Catégories de livres"""
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=10, default='📚')
    
    def __str__(self):
        return self.nom


class Livre(models.Model):
    """Livres disponibles à l'achat"""
    titre = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    auteur = models.CharField(max_length=200)
    editeur = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=13, blank=True)
    
    categorie = models.ForeignKey(CategorieLivre, on_delete=models.SET_NULL, null=True)
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, blank=True)
    
    description = models.TextField()
    
    # 🆕 PRIX VARIABLE POUR LES LIVRES
    prix = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Prix du livre (75 FCFA minimum ou plus selon le livre)"
    )
    
    # Fichiers
    couverture = models.ImageField(upload_to='livres/couvertures/', blank=True)
    fichier = models.FileField(
        upload_to='livres/fichiers/%Y/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    
    # Métadonnées
    nombre_pages = models.IntegerField(default=0)
    annee_publication = models.IntegerField(null=True, blank=True)
    langue = models.CharField(max_length=50, default='Français')
    
    # Stats
    nombre_ventes = models.IntegerField(default=0)
    note_moyenne = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    
    est_disponible = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_ajout']
    
    def __str__(self):
        return f"{self.titre} - {self.auteur}"