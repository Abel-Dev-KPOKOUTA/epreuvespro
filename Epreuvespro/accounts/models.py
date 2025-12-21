from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Modèle utilisateur personnalisé"""
    
    CLASSE_CHOICES = [
        ('6eme', '6ème'),
        ('5eme', '5ème'),
        ('4eme', '4ème'),
        ('3eme', '3ème'),
        ('seconde', 'Seconde'),
        ('premiere', 'Première'),
        ('terminale', 'Terminale'),
    ]
    
    telephone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="Téléphone"
    )
    classe = models.CharField(
        max_length=20, 
        choices=CLASSE_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name="Classe"
    )
    photo = models.ImageField(
        upload_to='users/photos/', 
        blank=True, 
        null=True, 
        verbose_name="Photo de profil"
    )
    date_inscription = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date d'inscription"
    )
    
    # IMPORTANT : Corrige le conflit de related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',  # ← Ajout du related_name
        related_query_name='customuser',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',  # ← Ajout du related_name
        related_query_name='customuser',
    )
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    
    def __str__(self):
        return self.email or self.username