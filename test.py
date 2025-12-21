import os
import django
import sys

# Configure Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Epreuvespro.settings')
django.setup()

from django.utils.text import slugify
from epreuves.models import Classe, Matiere, CategorieEpreuve, Epreuve, Corrige
from django.core.files.base import ContentFile

def create_test_data():
    print("🎯 Création de données de test pour EpreuvesPro...")
    
    # 1. Créer une classe de test
    classe, _ = Classe.objects.get_or_create(
        nom='6eme',
        defaults={
            'niveau_ordre': 1,
            'cycle': 'college',
            'icone': '📚',
            'description': 'Classe de 6ème pour tests'
        }
    )
    print(f"📚 Classe: {classe.get_nom_display()}")
    
    # 2. Créer une matière de test
    matiere, _ = Matiere.objects.get_or_create(
        nom='Mathématiques Test',
        defaults={
            'slug': 'mathematiques-test',
            'icone': '➕',
            'couleur': '#3B82F6'
        }
    )
    matiere.classes.add(classe)
    print(f"📖 Matière: {matiere.nom}")
    
    # 3. Créer une catégorie
    categorie, _ = CategorieEpreuve.objects.get_or_create(
        nom='trimestre1',
        defaults={}
    )
    
    # 4. Créer une épreuve
    epreuve = Epreuve.objects.create(
        titre='Test Mathématiques 6ème',
        slug='test-mathematiques-6eme',
        classe=classe,
        matiere=matiere,
        categorie=categorie,
        annee_scolaire='2024-2025',
        duree=45,
        nombre_pages=3,
        prix_unitaire=15.00,
        est_gratuit=False,
        disponible_achat_unitaire=True,
        disponible_abonnement=True,
    )
    
    # Créer un fichier PDF simulé
    pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n...'
    epreuve.fichier.save('test.pdf', ContentFile(pdf_content))
    
    print(f"✅ Épreuve créée: {epreuve.titre}")
    print(f"   ID: {epreuve.id}")
    print(f"   Slug: {epreuve.slug}")
    print(f"   URL: /epreuves/detail/{epreuve.slug}/")
    
    # 5. Optionnel: Créer un corrigé
    corrige = Corrige.objects.create(
        epreuve=epreuve,
        prix_unitaire=15.00,
        type_corrige='detaille',
        auteur='Système de Test',
    )
    corrige.fichier.save('corrige_test.pdf', ContentFile(pdf_content))
    
    print(f"✅ Corrigé créé pour l'épreuve")
    
    print("\n🎉 Test réussi !")
    print(f"Vous pouvez maintenant accéder à: http://localhost:8000/epreuves/detail/{epreuve.slug}/")
    print("\nPour supprimer les données de test:")
    print(f"python manage.py shell")
    print(f">>> from epreuves.models import Epreuve")
    print(f">>> Epreuve.objects.filter(slug='test-mathematiques-6eme').delete()")

if __name__ == '__main__':
    create_test_data()