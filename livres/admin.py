# livres/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import CategorieLivre, Livre


@admin.register(CategorieLivre)
class CategorieLivreAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'icone')
    search_fields = ('nom',)
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ('nom',)
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('nom', 'slug', 'icone', 'description')
        }),
    )


@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = (
        'titre', 
        'auteur',
        'editeur',
        'categorie',
        'classe',
        'prix',
        'note_moyenne',
        'nombre_ventes',
        'est_disponible',
        'apercu_couverture',
        'date_ajout'
    )
    
    list_filter = (
        'categorie', 
        'classe',
        'est_disponible', 
        'langue',
        'date_ajout'
    )
    
    search_fields = ('titre', 'auteur', 'editeur', 'description', 'isbn')
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ('nombre_ventes', 'note_moyenne', 'date_ajout', 'apercu_couverture_large')
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'slug', 'auteur', 'editeur', 'isbn')
        }),
        ('Classification', {
            'fields': ('categorie', 'classe')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Fichiers', {
            'fields': ('couverture', 'apercu_couverture_large', 'fichier')
        }),
        ('Métadonnées', {
            'fields': ('nombre_pages', 'annee_publication', 'langue')
        }),
        ('Prix et disponibilité', {
            'fields': ('prix', 'est_disponible')
        }),
        ('Statistiques', {
            'fields': ('nombre_ventes', 'note_moyenne', 'date_ajout'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-date_ajout',)
    
    # Actions personnalisées
    actions = ['marquer_disponible', 'marquer_indisponible']
    
    def apercu_couverture(self, obj):
        """Miniature de la couverture dans la liste"""
        if obj.couverture:
            return format_html(
                '<img src="{}" width="50" height="70" style="object-fit: cover; border-radius: 4px;" />',
                obj.couverture.url
            )
        return "Pas de couverture"
    apercu_couverture.short_description = 'Couverture'
    
    def apercu_couverture_large(self, obj):
        """Aperçu large de la couverture dans le formulaire"""
        if obj.couverture:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 400px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />',
                obj.couverture.url
            )
        return "Aucune couverture uploadée"
    apercu_couverture_large.short_description = 'Aperçu de la couverture'
    
    def marquer_disponible(self, request, queryset):
        """Action pour marquer les livres comme disponibles"""
        updated = queryset.update(est_disponible=True)
        self.message_user(request, f'{updated} livre(s) marqué(s) comme disponible(s).')
    marquer_disponible.short_description = "✓ Marquer comme disponible"
    
    def marquer_indisponible(self, request, queryset):
        """Action pour marquer les livres comme indisponibles"""
        updated = queryset.update(est_disponible=False)
        self.message_user(request, f'{updated} livre(s) marqué(s) comme indisponible(s).')
    marquer_indisponible.short_description = "✗ Marquer comme indisponible"