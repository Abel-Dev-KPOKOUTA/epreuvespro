# epreuves/admin.py
from django.contrib import admin
from .models import Classe, Matiere, CategorieEpreuve, Epreuve, Corrige


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'get_nom_display', 'cycle', 'niveau_ordre', 'nb_epreuves')
    list_filter = ('cycle',)
    search_fields = ('nom',)
    ordering = ('niveau_ordre',)
    
    def get_nom_display(self, obj):
        return obj.get_nom_display()
    get_nom_display.short_description = 'Nom affiché'


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'icone', 'couleur')
    search_fields = ('nom',)
    prepopulated_fields = {'slug': ('nom',)}
    filter_horizontal = ('classes',)
    ordering = ('nom',)


@admin.register(CategorieEpreuve)
class CategorieEpreuveAdmin(admin.ModelAdmin):
    list_display = ('nom', 'get_nom_display')
    
    def get_nom_display(self, obj):
        return obj.get_nom_display()
    get_nom_display.short_description = 'Nom affiché'


@admin.register(Epreuve)
class EpreuveAdmin(admin.ModelAdmin):
    list_display = (
        'titre', 
        'classe', 
        'matiere', 
        'categorie', 
        'annee_scolaire',
        'prix_unitaire',
        'est_gratuit',
        'nombre_telechargements',
        'date_ajout'
    )
    list_filter = (
        'classe', 
        'matiere', 
        'categorie', 
        'est_gratuit', 
        'disponible_achat_unitaire',
        'disponible_abonnement',
        'annee_scolaire'
    )
    search_fields = ('titre', 'annee_scolaire')
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ('nombre_telechargements', 'nombre_achats', 'date_ajout', 'date_modification')
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'slug', 'classe', 'matiere', 'categorie', 'annee_scolaire')
        }),
        ('Fichier', {
            'fields': ('fichier',)
        }),
        ('Métadonnées', {
            'fields': ('duree', 'coefficient', 'nombre_pages')
        }),
        ('Tarification', {
            'fields': ('prix_unitaire', 'est_gratuit', 'disponible_achat_unitaire', 'disponible_abonnement')
        }),
        ('Statistiques', {
            'fields': ('nombre_telechargements', 'nombre_achats', 'date_ajout', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-date_ajout',)


@admin.register(Corrige)
class CorrigeAdmin(admin.ModelAdmin):
    list_display = (
        'epreuve', 
        'type_corrige', 
        'prix_unitaire',
        'auteur',
        'date_ajout'
    )
    list_filter = ('type_corrige', 'date_ajout')
    search_fields = ('epreuve__titre', 'auteur')
    readonly_fields = ('date_ajout',)
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('epreuve', 'type_corrige', 'auteur')
        }),
        ('Fichier', {
            'fields': ('fichier',)
        }),
        ('Tarification', {
            'fields': ('prix_unitaire',)
        }),
        ('Statistiques', {
            'fields': ('date_ajout',),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-date_ajout',)